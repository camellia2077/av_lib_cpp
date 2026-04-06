// core/app/application.hpp
#ifndef APPLICATION_HPP
#define APPLICATION_HPP

#include <memory>
#include <string>
#include <vector>

#include "core/ports/i_database_catalog.hpp"

enum class ResultCode {
  kIdle,
  kWelcome,
  kDbLoadSuccess,
  kDbSwitched,
  kDbCreated,
  kAddCompleted,
  kQueryCompleted,
  kImportCompleted
};

enum class ErrorCode {
  kNone,
  kDbNotExist,
  kDbCreateFailed,
  kDbNameExists,
  kDbNameEmpty,
  kAddIdEmpty,
  kQueryIdEmpty,
  kIdInvalid,
  kFileOpenFailed,
  kFileEmpty
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
  void LoadDatabase();
  auto PerformAdd(const std::vector<std::string>& ids) -> AddResult;
  auto PerformQuery(const std::string& input) -> QueryResult;
  void PerformCreateDatabase(const std::string& new_db_name);
  void SetCurrentDatabase(const std::string& db_name);
  auto PerformImportLines(const std::vector<std::string>& lines)
      -> ImportResult;
  auto FetchAllIds(std::vector<std::string>& out_ids) -> bool;

  // --- Status Getters and Setters ---
  [[nodiscard]] auto GetLastResult() const -> ResultCode;
  [[nodiscard]] auto GetLastError() const -> ErrorCode;
  [[nodiscard]] auto GetInfoMessage() const -> const std::string&;
  [[nodiscard]] auto GetLastAddResult() const -> const AddResult&;
  [[nodiscard]] auto GetLastQueryResult() const -> const QueryResult&;
  [[nodiscard]] auto GetLastImportResult() const -> const ImportResult&;
  void SetError(ErrorCode error);
  void SetResult(ResultCode result);
  void ResetState(ResultCode result = ResultCode::kIdle);
  void SetInfoMessage(const std::string& message);

  // --- Data Getters ---
  [[nodiscard]] auto GetTotalRecords() const -> size_t;
  [[nodiscard]] auto GetDatabaseNames() const -> std::vector<std::string>;
  [[nodiscard]] auto GetCurrentDbName() const -> const std::string&;

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
