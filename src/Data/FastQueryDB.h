#pragma once

#include <string>
#include <vector>
#include <unordered_set>
#include <mutex>

class FastQueryDB {
public:
    // 构造函数，指定数据库文件路径
    explicit FastQueryDB(std::string filepath);

    // 从文件加载数据到内存，在程序启动时调用
    // 如果文件不存在，则会静默失败，这是一个正常情况
    void load();

    // 将内存中的数据安全地保存到文件
    // 返回true表示成功，false表示失败
    bool save();

    // 添加一个新的ID
    // 如果ID已存在，返回false；如果添加成功，返回true并自动保存
    bool add(const std::string& id);

    // 查询一个ID是否存在
    bool exists(const std::string& id) const;

    // 获取当前存储的ID总数
    size_t get_count() const;

private:
    std::string db_filepath_;
    std::unordered_set<std::string> id_set_;
    
    // 使用互斥锁来保证多线程场景下的数据安全（GUI操作是单线程，但这是良好实践）
    mutable std::mutex mtx_; 
};