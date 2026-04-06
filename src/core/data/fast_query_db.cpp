// core/data/fast_query_db.cpp
#include "core/data/fast_query_db.hpp"

#include <iostream>
#include <stdexcept>  // for std::runtime_error

// --- FastQueryDB 实现 ---

FastQueryDB::FastQueryDB(std::string filepath)
    : db_filepath_(std::move(filepath)) {
  if (sqlite3_open(db_filepath_.c_str(), &db_) != SQLITE_OK) {
    std::string err_msg = "无法打开数据库: ";
    err_msg += sqlite3_errmsg(db_);
    sqlite3_close(db_);
    throw std::runtime_error(err_msg);
  }
  InitializeDb();
}

FastQueryDB::~FastQueryDB() {
  if (add_stmt_) {
    sqlite3_finalize(add_stmt_);
  }
  if (exists_stmt_) {
    sqlite3_finalize(exists_stmt_);
  }
  if (count_stmt_) {
    sqlite3_finalize(count_stmt_);
  }
  if (db_) {
    sqlite3_close(db_);
  }
}

void FastQueryDB::InitializeDb() {
  const char* create_table_sql =
      "CREATE TABLE IF NOT EXISTS ids ("
      " id TEXT PRIMARY KEY NOT NULL"
      ");";

  char* err_msg = nullptr;
  if (sqlite3_exec(db_, create_table_sql, nullptr, nullptr, &err_msg) !=
      SQLITE_OK) {
    std::string error = "创建表失败: ";
    error += err_msg;
    sqlite3_free(err_msg);
    throw std::runtime_error(error);
  }

  const char* insert_sql = "INSERT OR IGNORE INTO ids (id) VALUES (?);";
  if (sqlite3_prepare_v2(db_, insert_sql, -1, &add_stmt_, nullptr) !=
      SQLITE_OK) {
    throw std::runtime_error("准备 INSERT 语句失败");
  }

  const char* select_sql = "SELECT 1 FROM ids WHERE id = ?;";
  if (sqlite3_prepare_v2(db_, select_sql, -1, &exists_stmt_, nullptr) !=
      SQLITE_OK) {
    throw std::runtime_error("准备 SELECT 语句失败");
  }

  const char* count_sql = "SELECT COUNT(*) FROM ids;";
  if (sqlite3_prepare_v2(db_, count_sql, -1, &count_stmt_, nullptr) !=
      SQLITE_OK) {
    throw std::runtime_error("准备 COUNT 语句失败");
  }
}

auto FastQueryDB::Add(const std::string& id) -> bool {
  sqlite3_bind_text(add_stmt_, 1, id.c_str(), -1, SQLITE_STATIC);

  bool success = false;
  if (sqlite3_step(add_stmt_) == SQLITE_DONE) {
    if (sqlite3_changes(db_) > 0) {
      success = true;
    }
  }

  sqlite3_reset(add_stmt_);
  return success;
}

auto FastQueryDB::Exists(const std::string& id) const -> bool {
  sqlite3_bind_text(exists_stmt_, 1, id.c_str(), -1, SQLITE_STATIC);

  bool found = false;
  if (sqlite3_step(exists_stmt_) == SQLITE_ROW) {
    found = true;
  }

  sqlite3_reset(exists_stmt_);
  return found;
}

auto FastQueryDB::GetCount() const -> size_t {
  size_t count = 0;
  if (sqlite3_step(count_stmt_) == SQLITE_ROW) {
    count = sqlite3_column_int(count_stmt_, 0);
  }
  sqlite3_reset(count_stmt_);
  return count;
}

auto FastQueryDB::GetAllIds() const -> std::vector<std::string> {
  std::vector<std::string> ids;
  const char* select_all_sql = "SELECT id FROM ids;";
  sqlite3_stmt* stmt = nullptr;
  if (sqlite3_prepare_v2(db_, select_all_sql, -1, &stmt, nullptr) !=
      SQLITE_OK) {
    return ids;
  }

  while (sqlite3_step(stmt) == SQLITE_ROW) {
    const unsigned char* text = sqlite3_column_text(stmt, 0);
    if (text != nullptr) {
      ids.emplace_back(reinterpret_cast<const char*>(text));
    }
  }
  sqlite3_finalize(stmt);
  return ids;
}

void FastQueryDB::BeginTransaction() {
  sqlite3_exec(db_, "BEGIN TRANSACTION;", nullptr, nullptr, nullptr);
}

void FastQueryDB::CommitTransaction() {
  sqlite3_exec(db_, "COMMIT;", nullptr, nullptr, nullptr);
}

void FastQueryDB::RollbackTransaction() {
  sqlite3_exec(db_, "ROLLBACK;", nullptr, nullptr, nullptr);
}
