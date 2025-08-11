#pragma once

#include <string>
#include <vector>
#include <unordered_set>
#include <mutex>

// 负责在内存中管理ID集合，并提供线程安全的操作
class IDRepository {
public:
    IDRepository() = default;

    // 尝试添加一个ID，如果成功（ID原先不存在），返回true
    bool add(const std::string& id);

    // 检查一个ID是否存在
    bool exists(const std::string& id) const;

    // 获取所有ID的副本，用于保存
    std::unordered_set<std::string> get_all() const;

    // 从一个集合加载所有ID，用于加载
    void load_from_collection(const std::unordered_set<std::string>& ids);

    // 获取当前记录总数
    size_t get_count() const;

private:
    std::unordered_set<std::string> id_set_;
    mutable std::mutex mtx_; 
};