// core/app/application.cpp
#include "core/app/application.hpp"

#include <stdexcept>
#include <vector>

#include "core/utils/validator.hpp"

// --- create_canonical_id 辅助函数 (保持不变) ---
namespace {
auto CreateCanonicalId(const std::string& raw_id) -> std::string {
  std::string canonical_id;
  canonical_id.reserve(raw_id.length());
  for (char c : raw_id) {
    if (Validator::IsAlphaChar(c) || Validator::IsDigitChar(c)) {
      canonical_id += c;
    }
  }
  return canonical_id;
}
}  // namespace

Application::Application(std::unique_ptr<IDatabaseCatalog> db_catalog)
    : db_manager_(std::move(db_catalog)) {
  if (!db_manager_) {
    throw std::invalid_argument("db_catalog");
  }
  ResetState(ResultCode::kWelcome);
}

Application::~Application() = default;

void Application::LoadDatabase() {
  db_manager_->LoadDefaultDatabase();
  SetResult(ResultCode::kDbLoadSuccess);
}

void Application::PerformCreateDatabase(const std::string& new_db_name) {
  SetError(ErrorCode::kNone);
  if (new_db_name.empty()) {
    SetError(ErrorCode::kDbNameEmpty);
    return;
  }

  std::string db_file_name = new_db_name;
  if (db_file_name.find(".sqlite3") == std::string::npos) {
    db_file_name += ".sqlite3";
  }

  if (db_manager_->DatabaseExists(db_file_name)) {
    SetError(ErrorCode::kDbNameExists);
    return;
  }

  if (db_manager_->CreateDatabase(new_db_name)) {
    SetResult(ResultCode::kDbCreated);
  } else {
    SetError(ErrorCode::kDbCreateFailed);
  }
}

auto Application::PerformAdd(const std::vector<std::string>& ids) -> AddResult {
  AddResult result;
  SetError(ErrorCode::kNone);
  IIdRepository* current_db = db_manager_->GetCurrentDb();
  if (current_db == nullptr) {
    SetError(ErrorCode::kDbNotExist);
    last_add_result_ = result;
    return result;
  }

  if (ids.empty()) {
    SetError(ErrorCode::kAddIdEmpty);
    last_add_result_ = result;
    return result;
  }

  result.target_db_name = db_manager_->GetCurrentDbName();

  current_db->BeginTransaction();
  try {
    for (const auto& id : ids) {
      if (id.empty()) {
        continue;
      }
      if (!Validator::IsValidIdFormat(id)) {
        result.invalid_format_count++;
      } else {
        std::string canonical_id = CreateCanonicalId(id);
        if (current_db->Add(canonical_id)) {
          result.success_count++;
        } else {
          result.exist_count++;
        }
      }
    }
    current_db->CommitTransaction();
  } catch (...) {
    current_db->RollbackTransaction();
    throw;
  }

  if (result.success_count == 0 && result.exist_count == 0 &&
      result.invalid_format_count == 0) {
    SetError(ErrorCode::kAddIdEmpty);
    last_add_result_ = result;
    return result;
  }

  SetResult(ResultCode::kAddCompleted);
  last_add_result_ = result;
  return result;
}

auto Application::PerformQuery(const std::string& input) -> QueryResult {
  QueryResult result;
  SetError(ErrorCode::kNone);
  IIdRepository* current_db = db_manager_->GetCurrentDb();
  if (current_db == nullptr) {
    SetError(ErrorCode::kDbNotExist);
    last_query_result_ = result;
    return result;
  }

  if (input.empty()) {
    SetError(ErrorCode::kQueryIdEmpty);
    last_query_result_ = result;
    return result;
  }

  result.target_db_name = db_manager_->GetCurrentDbName();

  if (!Validator::IsValidIdFormat(input)) {
    result.invalid_format_count = 1;
  } else {
    std::string canonical_id = CreateCanonicalId(input);
    if (current_db->Exists(canonical_id)) {
      result.found_count = 1;
    } else {
      result.not_found_count = 1;
    }
  }

  SetResult(ResultCode::kQueryCompleted);
  last_query_result_ = result;
  return result;
}

void Application::SetCurrentDatabase(const std::string& db_name) {
  SetError(ErrorCode::kNone);
  if (db_manager_->SwitchToDatabase(db_name)) {
    SetResult(ResultCode::kDbSwitched);
  } else {
    SetError(ErrorCode::kDbNotExist);
  }
}

auto Application::GetDatabaseNames() const -> std::vector<std::string> {
  return db_manager_->GetAllDbNames();
}

auto Application::GetCurrentDbName() const -> const std::string& {
  return db_manager_->GetCurrentDbName();
}

auto Application::GetTotalRecords() const -> size_t {
  IIdRepository* current_db = db_manager_->GetCurrentDb();
  return (current_db != nullptr) ? current_db->GetCount() : 0;
}

auto Application::GetLastResult() const -> ResultCode {
  return last_result_;
}

auto Application::GetLastError() const -> ErrorCode {
  return last_error_;
}

auto Application::GetInfoMessage() const -> const std::string& {
  return info_message_;
}

auto Application::GetLastAddResult() const -> const AddResult& {
  return last_add_result_;
}

auto Application::GetLastQueryResult() const -> const QueryResult& {
  return last_query_result_;
}

auto Application::GetLastImportResult() const -> const ImportResult& {
  return last_import_result_;
}

void Application::SetError(ErrorCode error) {
  last_error_ = error;
  info_message_.clear();
}

void Application::SetResult(ResultCode result) {
  last_result_ = result;
  last_error_ = ErrorCode::kNone;
  info_message_.clear();
}

void Application::ResetState(ResultCode result) {
  last_result_ = result;
  last_error_ = ErrorCode::kNone;
  info_message_.clear();
}

void Application::SetInfoMessage(const std::string& message) {
  info_message_ = message;
}

auto Application::PerformImportLines(const std::vector<std::string>& lines)
    -> ImportResult {
  ImportResult result;
  SetError(ErrorCode::kNone);
  IIdRepository* current_db = db_manager_->GetCurrentDb();
  if (current_db == nullptr) {
    SetError(ErrorCode::kDbNotExist);
    last_import_result_ = result;
    return result;
  }

  if (lines.empty()) {
    SetError(ErrorCode::kFileEmpty);
    last_import_result_ = result;
    return result;
  }

  result.target_db_name = db_manager_->GetCurrentDbName();

  current_db->BeginTransaction();
  try {
    for (const auto& line : lines) {
      if (!Validator::IsValidIdFormat(line)) {
        result.invalid_format_count++;
      } else {
        std::string canonical_id = CreateCanonicalId(line);
        if (current_db->Add(canonical_id)) {
          result.success_count++;
        } else {
          result.exist_count++;
        }
      }
    }
    current_db->CommitTransaction();
  } catch (...) {
    current_db->RollbackTransaction();
    throw;
  }

  SetResult(ResultCode::kImportCompleted);
  last_import_result_ = result;
  return result;
}

auto Application::FetchAllIds(std::vector<std::string>& out_ids) -> bool {
  SetError(ErrorCode::kNone);
  IIdRepository* current_db = db_manager_->GetCurrentDb();
  if (current_db == nullptr) {
    SetError(ErrorCode::kDbNotExist);
    return false;
  }
  out_ids = current_db->GetAllIds();
  return true;
}
