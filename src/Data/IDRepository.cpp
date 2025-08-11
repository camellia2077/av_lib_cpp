#include "IDRepository.h"

bool IDRepository::add(const std::string& id) {
    if (id.empty()) {
        return false;
    }
    std::lock_guard<std::mutex> lock(mtx_);
    auto const& [it, inserted] = id_set_.insert(id);
    return inserted;
}

bool IDRepository::exists(const std::string& id) const {
    if (id.empty()) {
        return false;
    }
    std::lock_guard<std::mutex> lock(mtx_);
    return id_set_.count(id) > 0;
}

std::unordered_set<std::string> IDRepository::get_all() const {
    std::lock_guard<std::mutex> lock(mtx_);
    return id_set_;
}

void IDRepository::load_from_collection(const std::unordered_set<std::string>& ids) {
    std::lock_guard<std::mutex> lock(mtx_);
    id_set_ = ids;
}

size_t IDRepository::get_count() const {
    std::lock_guard<std::mutex> lock(mtx_);
    return id_set_.size();
}