#pragma once

#include "Data/repository/IDRepository.h" // 包含新的数据核心类
#include <string>
#include <memory>

class FastQueryDB {
public:
    explicit FastQueryDB(std::string filepath);

    // 公共接口保持不变
    void load();
    bool save();
    bool add(const std::string& id);
    bool exists(const std::string& id) const;
    size_t get_count() const;

private:
    std::string db_filepath_;
    // 关键修改：不再直接持有数据和锁，而是持有一个Repository实例
    std::unique_ptr<IDRepository> repository_;
};