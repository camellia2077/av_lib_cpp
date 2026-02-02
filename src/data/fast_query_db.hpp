// data/fast_query_db.hpp
#ifndef FAST_QUERY_D_B_HPP
#define FAST_QUERY_D_B_HPP

#include <memory>
#include <string>

#include "ports/i_id_repository.hpp"
#include "sqlite3.h"

class FastQueryDB : public IIdRepository {
 public:
  explicit FastQueryDB(std::string filepath);
  ~FastQueryDB() override;

  FastQueryDB(const FastQueryDB&) = delete;
  auto operator=(const FastQueryDB&) -> FastQueryDB& = delete;

  auto Add(const std::string& id) -> bool override;
  [[nodiscard]] auto Exists(const std::string& id) const -> bool override;
  [[nodiscard]] auto GetCount() const -> size_t override;
  [[nodiscard]] auto GetAllIds() const -> std::vector<std::string> override;

  // --- Add these new methods for transaction control ---
  void BeginTransaction() override;
  void CommitTransaction() override;
  void RollbackTransaction() override;

 private:
  void InitializeDb();

  std::string db_filepath_;
  sqlite3* db_ = nullptr;
  sqlite3_stmt* add_stmt_ = nullptr;
  sqlite3_stmt* exists_stmt_ = nullptr;
  sqlite3_stmt* count_stmt_ = nullptr;
};
#endif
