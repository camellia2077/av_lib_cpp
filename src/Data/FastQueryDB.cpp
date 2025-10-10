// Data/FastQueryDB.cpp
#include "FastQueryDB.hpp"
#include <iostream>
#include <stdexcept> // for std::runtime_error

// --- FastQueryDB 实现 ---

FastQueryDB::FastQueryDB(std::string filepath)
    : db_filepath_(std::move(filepath))
{
    // 在构造函数中打开数据库连接
    if (sqlite3_open(db_filepath_.c_str(), &db_) != SQLITE_OK) {
        std::string err_msg = "无法打开数据库: ";
        err_msg += sqlite3_errmsg(db_);
        sqlite3_close(db_); // 即使打开失败，也要尝试关闭
        throw std::runtime_error(err_msg);
    }
    initialize_db();
}

FastQueryDB::~FastQueryDB() {
    // 在析构函数中释放所有资源
    sqlite3_finalize(add_stmt_);
    sqlite3_finalize(exists_stmt_);
    sqlite3_finalize(count_stmt_);
    sqlite3_close(db_);
}

void FastQueryDB::initialize_db() {
    // 1. 创建表 (如果不存在)
    const char* create_table_sql =
        "CREATE TABLE IF NOT EXISTS ids ("
        " id TEXT PRIMARY KEY NOT NULL"
        ");";

    char* err_msg = nullptr;
    if (sqlite3_exec(db_, create_table_sql, nullptr, nullptr, &err_msg) != SQLITE_OK) {
        std::string error = "创建表失败: ";
        error += err_msg;
        sqlite3_free(err_msg);
        throw std::runtime_error(error);
    }

    // 3. 准备预编译语句
    const char* insert_sql = "INSERT OR IGNORE INTO ids (id) VALUES (?);";
    if (sqlite3_prepare_v2(db_, insert_sql, -1, &add_stmt_, nullptr) != SQLITE_OK) {
        throw std::runtime_error("准备 INSERT 语句失败");
    }

    const char* select_sql = "SELECT 1 FROM ids WHERE id = ?;";
    if (sqlite3_prepare_v2(db_, select_sql, -1, &exists_stmt_, nullptr) != SQLITE_OK) {
        throw std::runtime_error("准备 SELECT 语句失败");
    }
    
    const char* count_sql = "SELECT COUNT(*) FROM ids;";
    if (sqlite3_prepare_v2(db_, count_sql, -1, &count_stmt_, nullptr) != SQLITE_OK) {
        throw std::runtime_error("准备 COUNT 语句失败");
    }
}


bool FastQueryDB::add(const std::string& id) {
    // 绑定参数并执行
    sqlite3_bind_text(add_stmt_, 1, id.c_str(), -1, SQLITE_STATIC);
    
    bool success = false;
    if (sqlite3_step(add_stmt_) == SQLITE_DONE) {
        // 检查是否有行被改变
        if (sqlite3_changes(db_) > 0) {
            success = true;
        }
    }

    // 重置语句以便下次使用
    sqlite3_reset(add_stmt_);
    return success;
}

bool FastQueryDB::exists(const std::string& id) const {
    sqlite3_bind_text(exists_stmt_, 1, id.c_str(), -1, SQLITE_STATIC);
    
    bool found = false;
    if (sqlite3_step(exists_stmt_) == SQLITE_ROW) {
        found = true;
    }
    
    sqlite3_reset(exists_stmt_);
    return found;
}

size_t FastQueryDB::get_count() const {
    size_t count = 0;
    if (sqlite3_step(count_stmt_) == SQLITE_ROW) {
        count = sqlite3_column_int(count_stmt_, 0);
    }
    sqlite3_reset(count_stmt_);
    return count;
}

// --- Add these new method implementations at the end ---
void FastQueryDB::begin_transaction() {
    sqlite3_exec(db_, "BEGIN TRANSACTION;", nullptr, nullptr, nullptr);
}

void FastQueryDB::commit_transaction() {
    sqlite3_exec(db_, "COMMIT;", nullptr, nullptr, nullptr);
}

void FastQueryDB::rollback_transaction() {
    sqlite3_exec(db_, "ROLLBACK;", nullptr, nullptr, nullptr);
}