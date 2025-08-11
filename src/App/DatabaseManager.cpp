#include "DatabaseManager.h"
#include <filesystem> // 引入 <filesystem>
#include <string>     // 确保包含 <string>

DatabaseManager::DatabaseManager() {
    // 默认数据库名称
    current_db_name_ = "database.bin";
}

void DatabaseManager::load_default_database() {
    // 加载默认数据库
    dbs_[current_db_name_] = std::make_unique<FastQueryDB>(current_db_name_);
    dbs_[current_db_name_]->load();
}

bool DatabaseManager::create_database(const std::string& db_name_raw) {
    std::string new_db_name = db_name_raw;

    // --- 修改点：使用 C++23 的 std::string::contains ---
    // 如果原始名称不包含 ".bin"，则给它添加一个
    if (!db_name_raw.contains(".bin")) {
        new_db_name += ".bin";
    }
    // --- 修改结束 ---

    if (dbs_.count(new_db_name)) {
        return false; // 数据库已存在
    }

    auto db = std::make_unique<FastQueryDB>(new_db_name);
    if (db->save()) { // 调用save()来创建物理文件
        dbs_[new_db_name] = std::move(db);
        current_db_name_ = new_db_name; // 创建成功后自动切换
        return true;
    }
    
    return false; // 创建失败
}

bool DatabaseManager::switch_to_database(const std::string& db_name) {
    if (dbs_.count(db_name)) {
        current_db_name_ = db_name;
        return true;
    }
    return false;
}

bool DatabaseManager::database_exists(const std::string& db_name) const {
    // C++20 之后，map::count 在性能上和 map::contains 几乎一样
    return dbs_.count(db_name) > 0;
}

FastQueryDB* DatabaseManager::get_current_db() const {
    if (dbs_.count(current_db_name_)) {
        return dbs_.at(current_db_name_).get();
    }
    return nullptr;
}

const std::string& DatabaseManager::get_current_db_name() const {
    return current_db_name_;
}

std::vector<std::string> DatabaseManager::get_all_db_names() const {
    std::vector<std::string> names;
    for(const auto& pair : dbs_) {
        names.push_back(pair.first);
    }
    return names;
}