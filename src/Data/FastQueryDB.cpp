#include "common/pch.h"
#include "FastQueryDB.h"
#include <fstream>
#include <iostream>
#include <cstdio> // 用于 std::rename 和 std::remove

FastQueryDB::FastQueryDB(std::string filepath) : db_filepath_(std::move(filepath)) {}

void FastQueryDB::load() {
    std::lock_guard<std::mutex> lock(mtx_);
    
    std::ifstream infile(db_filepath_, std::ios::binary);
    if (!infile) {
        // 文件不存在是正常情况，比如第一次运行
        return;
    }

    id_set_.clear();
    while (infile) {
        // 读取长度前缀 (我们用 uint32_t 存储长度)
        uint32_t len;
        infile.read(reinterpret_cast<char*>(&len), sizeof(len));

        if (infile.eof()) {
            break; // 正常到达文件末尾
        }

        // 根据长度读取字符串内容
        std::string id(len, '\0');
        infile.read(&id[0], len);
        
        if (infile.good()) {
            id_set_.insert(id);
        }
    }
    std::cout << "数据库加载完成，共 " << id_set_.size() << " 条记录。" << std::endl;
}

bool FastQueryDB::save() {
    std::lock_guard<std::mutex> lock(mtx_);

    // “影子文件”策略：先写入临时文件
    std::string tmp_filepath = db_filepath_ + ".tmp";
    std::ofstream outfile(tmp_filepath, std::ios::binary | std::ios::trunc);

    if (!outfile) {
        std::cerr << "错误：无法创建临时数据库文件 " << tmp_filepath << std::endl;
        return false;
    }

    // 遍历内存中的set，写入文件
    for (const auto& id : id_set_) {
        // 写入长度前缀
        uint32_t len = id.length();
        outfile.write(reinterpret_cast<const char*>(&len), sizeof(len));
        // 写入字符串数据
        outfile.write(id.c_str(), len);
    }
    
    outfile.close();
    if (!outfile.good()) {
        std::cerr << "错误：写入临时文件失败。" << std::endl;
        return false;
    }

    // 关键步骤：用临时文件替换原始文件，这是一个原子或接近原子的操作
    // 1. 先删除旧文件 (如果存在)
    std::remove(db_filepath_.c_str());
    // 2. 将临时文件重命名为正式文件
    if (std::rename(tmp_filepath.c_str(), db_filepath_.c_str()) != 0) {
        std::cerr << "错误：无法将临时文件重命名为正式文件。" << std::endl;
        // 尝试删除临时文件以清理
        std::remove(tmp_filepath.c_str());
        return false;
    }
    
    return true;
}

bool FastQueryDB::add(const std::string& id) {
    if (id.empty()) {
        return false;
    }

    std::lock_guard<std::mutex> lock(mtx_);
    
    // 尝试插入，.second 会告诉我们是否插入了新元素
    auto const& [it, inserted] = id_set_.insert(id);

    if (inserted) {
        // 如果插入成功，则立即保存
        // 在实际应用中，为了避免频繁IO，也可以设计成定时或手动保存
        // 这里为了简单和数据一致性，我们选择立即保存
        // 注意：这里的save调用会再次锁mutex，需要使用std::recursive_mutex，或者先解锁再保存。
        // 为简化，我们直接调用内部逻辑，或者将save分离为带锁和不带锁的版本。
        // 一个简单的解决方案是在调用save之前，就释放锁，因为数据已经更新到set里了。
        // 但这里为了代码简单，我们暂时忽略这个重入锁问题，因为save函数内的锁是多余的。
        // 更好的设计是有一个 private save_nolock()
        
        // 我们在这里手动模拟保存逻辑，避免重入锁
        std::string tmp_filepath = db_filepath_ + ".tmp";
        std::ofstream outfile(tmp_filepath, std::ios::binary | std::ios::trunc);
        for (const auto& current_id : id_set_) {
            uint32_t len = current_id.length();
            outfile.write(reinterpret_cast<const char*>(&len), sizeof(len));
            outfile.write(current_id.c_str(), len);
        }
        outfile.close();
        std::remove(db_filepath_.c_str());
        std::rename(tmp_filepath.c_str(), db_filepath_.c_str());
        
        return true;
    }

    return false; // ID 已存在
}

bool FastQueryDB::exists(const std::string& id) const {
    if (id.empty()) {
        return false;
    }
    std::lock_guard<std::mutex> lock(mtx_);
    return id_set_.count(id) > 0;
}

size_t FastQueryDB::get_count() const {
    std::lock_guard<std::mutex> lock(mtx_);
    return id_set_.size();
}