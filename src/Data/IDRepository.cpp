#include "IDRepository.h"
#include <algorithm> // for std::transform
#include <cctype>    // for std::tolower

// 内部辅助函数，用于将字符串转换为小写
namespace {
    std::string to_lower(std::string s) {
        std::transform(s.begin(), s.end(), s.begin(),
                       [](unsigned char c){ return std::tolower(c); });
        return s;
    }
}

bool IDRepository::add(const std::string& id) {
    if (id.empty()) {
        return false;
    }
    // 转换为小写再进行操作
    std::string lower_id = to_lower(id);
    std::lock_guard<std::mutex> lock(mtx_);
    auto const& [it, inserted] = id_set_.insert(lower_id);
    return inserted;
}

bool IDRepository::exists(const std::string& id) const {
    if (id.empty()) {
        return false;
    }
    // 转换为小写再进行操作
    std::string lower_id = to_lower(id);
    std::lock_guard<std::mutex> lock(mtx_);
    return id_set_.count(lower_id) > 0;
}

std::unordered_set<std::string> IDRepository::get_all() const {
    std::lock_guard<std::mutex> lock(mtx_);
    return id_set_;
}

void IDRepository::load_from_collection(const std::unordered_set<std::string>& ids) {
    // 创建一个新的、全部小写的集合
    std::unordered_set<std::string> lower_case_ids;
    lower_case_ids.reserve(ids.size());
    for (const auto& id : ids) {
        if (!id.empty()) {
            lower_case_ids.insert(to_lower(id));
        }
    }
    
    // 加锁并替换旧的集合
    std::lock_guard<std::mutex> lock(mtx_);
    id_set_ = std::move(lower_case_ids);
}

size_t IDRepository::get_count() const {
    std::lock_guard<std::mutex> lock(mtx_);
    return id_set_.size();
}