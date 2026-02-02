// app/application.hpp
#ifndef APPLICATION_HPP
#define APPLICATION_HPP

#include "ports/i_database_catalog.hpp"
#include <memory>
#include <string>
#include <vector>

enum class ResultCode {
  Idle,
  Welcome,
  DBLoadSuccess,
  DBSwitched,
  DBCreated,
  AddCompleted,
  QueryCompleted,
  ImportCompleted
};

enum class ErrorCode {
  None,
  DBNotExist,
  DBCreateFailed,
  DBNameExists,
  DBNameEmpty,
  AddIDEmpty,
  QueryIDEmpty,
  IdInvalid,
  FileOpenFailed,
  FileEmpty
};

struct AddResult {
  size_t success_count = 0;
  size_t exist_count = 0;
  size_t invalid_format_count = 0;
  std::string target_db_name;
};

struct QueryResult {
  size_t found_count = 0;
  size_t not_found_count = 0;
  size_t invalid_format_count = 0;
  std::string target_db_name;
};

struct ImportResult {
  size_t success_count = 0;
  size_t exist_count = 0;
  size_t invalid_format_count = 0;
  std::string target_db_name;
};

class Application {
public:
  explicit Application(std::unique_ptr<IDatabaseCatalog> db_catalog);
  ~Application();

  // --- Business Logic ---
  void load_database();
  AddResult perform_add(const std::vector<std::string> &ids);
  QueryResult perform_query(const std::string &input);
  void perform_create_database(const std::string &new_db_name);
  void set_current_database(const std::string &db_name);
  ImportResult perform_import_lines(const std::vector<std::string> &lines);
  bool fetch_all_ids(std::vector<std::string> &out_ids);

  // --- Status Getters and Setters ---
  ResultCode get_last_result() const;
  ErrorCode get_last_error() const;
  const std::string &get_info_message() const;
  const AddResult &get_last_add_result() const;
  const QueryResult &get_last_query_result() const;
  const ImportResult &get_last_import_result() const;
  void set_error(ErrorCode error);
  void set_result(ResultCode result);
  void reset_state(ResultCode result = ResultCode::Idle);
  void set_info_message(const std::string &message);

  // --- Data Getters ---
  size_t get_total_records() const;
  std::vector<std::string> get_database_names() const;
  const std::string &get_current_db_name() const;

private:
  std::unique_ptr<IDatabaseCatalog> db_manager_;
  ResultCode last_result_;
  ErrorCode last_error_;
  std::string info_message_;
  AddResult last_add_result_;
  QueryResult last_query_result_;
  ImportResult last_import_result_;
};
#endif
