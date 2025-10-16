// App/Application.cpp
#include "Application.hpp"
#include "IO/TextFileReader.hpp"
#include "Utils/Validator.hpp"
#include <vector>
#include <sstream>
#include <filesystem>
#include <fstream>
#include <iostream>
// --- [修正] 移除 <chrono>，因为我们不再使用时间戳 ---

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

// ... load_database, perform_create_database 等函数保持不变 ...
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


// --- [修正] perform_add 方法恢复原状 ---
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

    current_db->begin_transaction();
    try {
        while (ss >> id) {
            processed_count++;
            if (!Validator::isValidIDFormat(id)) {
                last_op_result_.invalid_format_count++;
            } else {
                std::string canonical_id = create_canonical_id(id);
                // --- 只传递一个参数 ---
                if (current_db->add(canonical_id)) {
                    last_op_result_.success_count++;
                } else {
                    last_op_result_.exist_count++;
                }
            }
        }
        current_db->commit_transaction();
    } catch (...) {
        current_db->rollback_transaction();
        throw;
    }

    if (processed_count == 0) {
        status_ = AppStatus::ErrorAddIDEmpty;
        return;
    }

    status_ = AppStatus::AddCompleted;
}

// ... perform_query 和其他 getter/setter 保持不变 ...
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


// --- [修正] perform_import_from_file 方法恢复原状 ---
void Application::perform_import_from_file(const std::string& filepath) {
    if (filepath.empty()) {
        return;
    }

    FastQueryDB* current_db = db_manager_->get_current_db();
    if (!current_db) {
        status_ = AppStatus::ErrorDBNotExist;
        return;
    }

    std::vector<std::string> lines;
    try {
        lines = IO::TextFileReader::read_all_lines(filepath);
    } catch (const FileOpenException& e) {
        std::cerr << e.what() << std::endl;
        status_ = AppStatus::ErrorFileOpenFailed;
        return;
    }

    if (lines.empty()) {
        status_ = AppStatus::ErrorFileEmpty;
        return;
    }

    last_op_result_ = {};
    last_op_result_.target_db_name = db_manager_->get_current_db_name();
    
    // --- 移除时间戳获取逻辑 ---

    current_db->begin_transaction();
    try {
        for (const auto& line : lines) {
            if (!Validator::isValidIDFormat(line)) {
                last_op_result_.invalid_format_count++;
            } else {
                std::string canonical_id = create_canonical_id(line);
                // --- 只传递一个参数 ---
                if (current_db->add(canonical_id)) {
                    last_op_result_.success_count++;
                } else {
                    last_op_result_.exist_count++;
                }
            }
        }
        current_db->commit_transaction();
    } catch (...) {
        current_db->rollback_transaction();
        throw;
    }

    status_ = AppStatus::ImportCompleted;
}