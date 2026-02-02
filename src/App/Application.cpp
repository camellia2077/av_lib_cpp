// app/application.cpp
#include "application.hpp"
#include "utils/validator.hpp"
#include <stdexcept>
#include <vector>

// --- create_canonical_id 辅助函数 (保持不变) ---
namespace {
std::string create_canonical_id(const std::string &raw_id) {
  std::string canonical_id;
  canonical_id.reserve(raw_id.length());
  for (char c : raw_id) {
    if (Validator::is_alpha_char(c) || Validator::is_digit_char(c)) {
      canonical_id += c;
    }
  }
  return canonical_id;
}
} // namespace

Application::Application(std::unique_ptr<IDatabaseCatalog> db_catalog)
    : db_manager_(std::move(db_catalog)) {
  if (!db_manager_) {
    throw std::invalid_argument("db_catalog");
  }
  reset_state(ResultCode::Welcome);
}

Application::~Application() = default;

// ... load_database, perform_create_database 等函数保持不变 ...
void Application::load_database() {
  db_manager_->load_default_database();
  set_result(ResultCode::DBLoadSuccess);
}

void Application::perform_create_database(const std::string &new_db_name) {
  set_error(ErrorCode::None);
  if (new_db_name.empty()) {
    set_error(ErrorCode::DBNameEmpty);
    return;
  }

  std::string db_file_name = new_db_name;
  if (db_file_name.find(".sqlite3") == std::string::npos) {
    db_file_name += ".sqlite3";
  }

  if (db_manager_->database_exists(db_file_name)) {
    set_error(ErrorCode::DBNameExists);
    return;
  }

  if (db_manager_->create_database(new_db_name)) {
    set_result(ResultCode::DBCreated);
  } else {
    set_error(ErrorCode::DBCreateFailed);
  }
}

// --- [修正] perform_add 方法恢复原状 ---
AddResult Application::perform_add(const std::vector<std::string> &ids) {
  AddResult result;
  set_error(ErrorCode::None);
  IIdRepository *current_db = db_manager_->get_current_db();
  if (!current_db) {
    set_error(ErrorCode::DBNotExist);
    last_add_result_ = result;
    return result;
  }

  if (ids.empty()) {
    set_error(ErrorCode::AddIDEmpty);
    last_add_result_ = result;
    return result;
  }

  result.target_db_name = db_manager_->get_current_db_name();

  current_db->begin_transaction();
  try {
    for (const auto &id : ids) {
      if (id.empty()) {
        continue;
      }
      if (!Validator::isValidIDFormat(id)) {
        result.invalid_format_count++;
      } else {
        std::string canonical_id = create_canonical_id(id);
        // --- 只传递一个参数 ---
        if (current_db->add(canonical_id)) {
          result.success_count++;
        } else {
          result.exist_count++;
        }
      }
    }
    current_db->commit_transaction();
  } catch (...) {
    current_db->rollback_transaction();
    throw;
  }

  if (result.success_count == 0 && result.exist_count == 0 &&
      result.invalid_format_count == 0) {
    set_error(ErrorCode::AddIDEmpty);
    last_add_result_ = result;
    return result;
  }

  set_result(ResultCode::AddCompleted);
  last_add_result_ = result;
  return result;
}

// ... perform_query 和其他 getter/setter 保持不变 ...
QueryResult Application::perform_query(const std::string &input) {
  QueryResult result;
  set_error(ErrorCode::None);
  IIdRepository *current_db = db_manager_->get_current_db();
  if (!current_db) {
    set_error(ErrorCode::DBNotExist);
    last_query_result_ = result;
    return result;
  }

  if (input.empty()) {
    set_error(ErrorCode::QueryIDEmpty);
    last_query_result_ = result;
    return result;
  }

  result.target_db_name = db_manager_->get_current_db_name();

  if (!Validator::isValidIDFormat(input)) {
    result.invalid_format_count = 1;
  } else {
    std::string canonical_id = create_canonical_id(input);
    if (current_db->exists(canonical_id)) {
      result.found_count = 1;
    } else {
      result.not_found_count = 1;
    }
  }

  set_result(ResultCode::QueryCompleted);
  last_query_result_ = result;
  return result;
}

void Application::set_current_database(const std::string &db_name) {
  set_error(ErrorCode::None);
  if (db_manager_->switch_to_database(db_name)) {
    set_result(ResultCode::DBSwitched);
  } else {
    set_error(ErrorCode::DBNotExist);
  }
}

std::vector<std::string> Application::get_database_names() const {
  return db_manager_->get_all_db_names();
}

const std::string &Application::get_current_db_name() const {
  return db_manager_->get_current_db_name();
}

size_t Application::get_total_records() const {
  IIdRepository *current_db = db_manager_->get_current_db();
  return current_db ? current_db->get_count() : 0;
}

ResultCode Application::get_last_result() const { return last_result_; }

ErrorCode Application::get_last_error() const { return last_error_; }

const std::string &Application::get_info_message() const {
  return info_message_;
}

const AddResult &Application::get_last_add_result() const {
  return last_add_result_;
}

const QueryResult &Application::get_last_query_result() const {
  return last_query_result_;
}

const ImportResult &Application::get_last_import_result() const {
  return last_import_result_;
}

void Application::set_error(ErrorCode error) {
  last_error_ = error;
  info_message_.clear();
}

void Application::set_result(ResultCode result) {
  last_result_ = result;
  last_error_ = ErrorCode::None;
  info_message_.clear();
}

void Application::reset_state(ResultCode result) {
  last_result_ = result;
  last_error_ = ErrorCode::None;
  info_message_.clear();
}

void Application::set_info_message(const std::string &message) {
  info_message_ = message;
}

// --- [修正] perform_import_lines 方法恢复原状 ---
ImportResult
Application::perform_import_lines(const std::vector<std::string> &lines) {
  ImportResult result;
  set_error(ErrorCode::None);
  IIdRepository *current_db = db_manager_->get_current_db();
  if (!current_db) {
    set_error(ErrorCode::DBNotExist);
    last_import_result_ = result;
    return result;
  }

  if (lines.empty()) {
    set_error(ErrorCode::FileEmpty);
    last_import_result_ = result;
    return result;
  }

  result.target_db_name = db_manager_->get_current_db_name();

  // --- 移除时间戳获取逻辑 ---

  current_db->begin_transaction();
  try {
    for (const auto &line : lines) {
      if (!Validator::isValidIDFormat(line)) {
        result.invalid_format_count++;
      } else {
        std::string canonical_id = create_canonical_id(line);
        // --- 只传递一个参数 ---
        if (current_db->add(canonical_id)) {
          result.success_count++;
        } else {
          result.exist_count++;
        }
      }
    }
    current_db->commit_transaction();
  } catch (...) {
    current_db->rollback_transaction();
    throw;
  }

  set_result(ResultCode::ImportCompleted);
  last_import_result_ = result;
  return result;
}

bool Application::fetch_all_ids(std::vector<std::string> &out_ids) {
  set_error(ErrorCode::None);
  IIdRepository *current_db = db_manager_->get_current_db();
  if (!current_db) {
    set_error(ErrorCode::DBNotExist);
    return false;
  }
  out_ids = current_db->get_all_ids();
  return true;
}
