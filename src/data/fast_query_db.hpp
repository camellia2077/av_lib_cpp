// data/fast_query_db.hpp
#ifndef FAST_QUERY_D_B_HPP
#define FAST_QUERY_D_B_HPP

#include "ports/i_id_repository.hpp"
#include "sqlite3.h"
#include <memory>
#include <string>

class FastQueryDB : public IIdRepository {
public:
  explicit FastQueryDB(std::string filepath);
  ~FastQueryDB();

  FastQueryDB(const FastQueryDB &) = delete;
  FastQueryDB &operator=(const FastQueryDB &) = delete;

  bool add(const std::string &id) override;
  bool exists(const std::string &id) const override;
  size_t get_count() const override;
  std::vector<std::string> get_all_ids() const override;

  // --- Add these new methods for transaction control ---
  void begin_transaction() override;
  void commit_transaction() override;
  void rollback_transaction() override;

private:
  void initialize_db();

  std::string db_filepath_;
  sqlite3 *db_ = nullptr;
  sqlite3_stmt *add_stmt_ = nullptr;
  sqlite3_stmt *exists_stmt_ = nullptr;
  sqlite3_stmt *count_stmt_ = nullptr;
};
#endif
