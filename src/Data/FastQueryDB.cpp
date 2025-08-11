#include "FastQueryDB.h"
#include "DBSerializer.h" // 包含新的序列化工具类
#include <utility>

FastQueryDB::FastQueryDB(std::string filepath) 
    : db_filepath_(std::move(filepath)) 
{
    // 构造时创建数据仓库实例
    repository_ = std::make_unique<IDRepository>();
}

void FastQueryDB::load() {
    // 协调：调用序列化器加载数据，然后交给仓库
    auto id_set = DBSerializer::load(db_filepath_);
    repository_->load_from_collection(id_set);
}

bool FastQueryDB::save() {
    // 协调：从仓库获取所有数据，然后交给序列化器保存
    auto id_set = repository_->get_all();
    return DBSerializer::save(db_filepath_, id_set);
}

bool FastQueryDB::add(const std::string& id) {
    // 协调：先尝试在仓库中添加
    if (repository_->add(id)) {
        // 如果添加成功，则立即保存
        // 这种设计避免了在add和save之间持有锁，减少了锁的粒度
        return save();
    }
    return false; // ID已存在，添加失败
}

bool FastQueryDB::exists(const std::string& id) const {
    // 委托：直接调用仓库的查询方法
    return repository_->exists(id);
}

size_t FastQueryDB::get_count() const {
    // 委托：直接调用仓库的计数方法
    return repository_->get_count();
}