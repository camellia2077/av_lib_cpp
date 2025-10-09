#pragma once

#include <string>
#include <memory>
#include "sqlite3.h"

class FastQueryDB {
public:
    explicit FastQueryDB(std::string filepath);
    ~FastQueryDB();

    FastQueryDB(const FastQueryDB&) = delete;
    FastQueryDB& operator=(const FastQueryDB&) = delete;

    bool add(const std::string& id);
    bool exists(const std::string& id) const;
    size_t get_count() const;

    // --- Add these new methods for transaction control ---
    void begin_transaction();
    void commit_transaction();
    void rollback_transaction();

private:
    void initialize_db();

    std::string db_filepath_;
    sqlite3* db_ = nullptr;
    sqlite3_stmt* add_stmt_ = nullptr;
    sqlite3_stmt* exists_stmt_ = nullptr;
    sqlite3_stmt* count_stmt_ = nullptr;
};