// App/Application.cpp
#include "Application.hpp"
#include "Utils/Validator.hpp"
#include <vector>
#include <sstream>
#include <filesystem>
#include <fstream>

// --- create_canonical_id 辅助函数 (保持不变) ---
namespace {
    std::string create_canonical_id(const std::string& raw_id) {
        std::string canonical_id;
        canonical_id.reserve(raw_id.length());
        for (char c : raw_id) {
            if (Validator::is_alpha_char(c) || Validator::is_digit_char(c)) {
                canonical_id += c;
            }
        }
        return canonical_id;
    }
}

Application::Application()
    : status_(AppStatus::Welcome)
{
    db_manager_ = std::make_unique<DatabaseManager>();
}

void Application::load_database() {
    db_manager_->load_default_database();
    status_ = AppStatus::DBLoadSuccess;
}

void Application::perform_create_database(const std::string& new_db_name) {
    if (new_db_name.empty()) {
        status_ = AppStatus::ErrorDBNameEmpty;
        return;
    }

    std::string db_file_name = new_db_name;
    // 确保文件名以 .sqlite3 结尾
    if (db_file_name.find(".sqlite3") == std::string::npos) {
        db_file_name += ".sqlite3";
    }

    if (db_manager_->database_exists(db_file_name)) {
        status_ = AppStatus::ErrorDBNameExists;
        return;
    }

    if (db_manager_->create_database(new_db_name)) {
        status_ = AppStatus::DBCreated;
    } else {
        status_ = AppStatus::ErrorDBCreateFailed;
    }
}

// --- perform_add 方法 (几乎不变) ---
void Application::perform_add(const std::string& input) {
    FastQueryDB* current_db = db_manager_->get_current_db();
    if (!current_db) {
        status_ = AppStatus::ErrorDBNotExist;
        return;
    }
    
    if (input.empty()) {
        status_ = AppStatus::ErrorAddIDEmpty;
        return;
    }

    last_op_result_ = {};
    last_op_result_.target_db_name = db_manager_->get_current_db_name();

    std::stringstream ss(input);
    std::string id;
    int processed_count = 0;

    // --- SQLite 优化：使用事务 ---
    // sqlite3_exec(current_db->get_db_handle(), "BEGIN TRANSACTION;", nullptr, nullptr, nullptr);

    while (ss >> id) {
        processed_count++;
        if (!Validator::isValidIDFormat(id)) {
            last_op_result_.invalid_format_count++;
        } else {
            std::string canonical_id = create_canonical_id(id);
            if (current_db->add(canonical_id)) {
                last_op_result_.success_count++;
            } else {
                last_op_result_.exist_count++;
            }
        }
    }
    
    // sqlite3_exec(current_db->get_db_handle(), "COMMIT;", nullptr, nullptr, nullptr);


    if (processed_count == 0) {
        status_ = AppStatus::ErrorAddIDEmpty;
        return;
    }

    status_ = AppStatus::AddCompleted;
}

// --- 其他方法 (保持不变) ---
void Application::perform_query(const std::string& input) {
    FastQueryDB* current_db = db_manager_->get_current_db();
    if (!current_db) {
        status_ = AppStatus::ErrorDBNotExist;
        return;
    }

    if (input.empty()) {
        status_ = AppStatus::ErrorQueryIDEmpty;
        return;
    }
    
    last_op_result_ = {};
    last_op_result_.target_db_name = db_manager_->get_current_db_name();

    if (!Validator::isValidIDFormat(input)) {
        last_op_result_.invalid_format_count = 1;
    } else {
        std::string canonical_id = create_canonical_id(input);
        if (current_db->exists(canonical_id)) {
            last_op_result_.success_count = 1;
        } else {
            last_op_result_.not_found_count = 1;
        }
    }
    
    status_ = AppStatus::QueryCompleted;
}

void Application::set_current_database(const std::string& db_name) {
    if (db_manager_->switch_to_database(db_name)) {
        status_ = AppStatus::DBSwitched;
    } else {
        status_ = AppStatus::ErrorDBNotExist;
    }
}

std::vector<std::string> Application::get_database_names() const {
    return db_manager_->get_all_db_names();
}

const std::string& Application::get_current_db_name() const {
    return db_manager_->get_current_db_name();
}

size_t Application::get_total_records() const {
    FastQueryDB* current_db = db_manager_->get_current_db();
    return current_db ? current_db->get_count() : 0;
}

AppStatus Application::get_status() const {
    return status_;
}

const OperationResult& Application::get_operation_result() const {
    return last_op_result_;

}

void Application::set_status(AppStatus new_status) {
    status_ = new_status;
}

void Application::perform_import_from_file(const std::string& filepath) {
    if (filepath.empty()) {
        return;
    }

    FastQueryDB* current_db = db_manager_->get_current_db();
    if (!current_db) {
        status_ = AppStatus::ErrorDBNotExist;
        return;
    }

    std::ifstream file(filepath);
    if (!file.is_open()) {
        status_ = AppStatus::ErrorFileOpenFailed;
        return;
    }

    last_op_result_ = {};
    last_op_result_.target_db_name = db_manager_->get_current_db_name();

    std::string line;
    int processed_count = 0;

    current_db->begin_transaction(); // Start transaction for performance

    try {
        while (std::getline(file, line)) {
            if (line.empty()) continue;

            processed_count++;
            if (!Validator::isValidIDFormat(line)) {
                last_op_result_.invalid_format_count++;
            } else {
                std::string canonical_id = create_canonical_id(line);
                if (current_db->add(canonical_id)) {
                    last_op_result_.success_count++;
                } else {
                    last_op_result_.exist_count++;
                }
            }
        }
        current_db->commit_transaction(); // Commit all changes at once
    } catch (...) {
        current_db->rollback_transaction(); // Rollback if any error occurs
        throw;
    }

    if (processed_count == 0) {
        status_ = AppStatus::ErrorFileEmpty;
        return;
    }

    status_ = AppStatus::ImportCompleted;
}