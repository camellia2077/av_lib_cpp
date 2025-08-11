#include "Application.h"
#include "Utils/Validator.h"
#include <vector>
#include <sstream>

Application::Application() 
    : status_(AppStatus::Welcome)
{
    // 创建并拥有 DatabaseManager
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
    
    if (db_manager_->database_exists(new_db_name + ".bin")) {
        status_ = AppStatus::ErrorDBNameExists;
        return;
    }

    if (db_manager_->create_database(new_db_name)) {
        status_ = AppStatus::DBCreated;
    } else {
        status_ = AppStatus::ErrorDBCreateFailed;
    }
}

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

    std::stringstream ss(input);
    std::string id;
    last_op_result_ = {}; // 重置结果
    last_op_result_.target_db_name = db_manager_->get_current_db_name();

    while (ss >> id) {
        if (!Validator::isValidIDFormat(id)) {
            last_op_result_.invalid_format_count++;
        } else if (current_db->add(id)) {
            last_op_result_.success_count++;
        } else {
            last_op_result_.exist_count++;
        }
    }

    status_ = AppStatus::AddCompleted;
}

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

    std::stringstream ss(input);
    std::string id;
    last_op_result_ = {}; // 重置结果
    last_op_result_.target_db_name = db_manager_->get_current_db_name();

    while (ss >> id) {
        if (!Validator::isValidIDFormat(id)) {
            last_op_result_.invalid_format_count++;
        } else if (current_db->exists(id)) {
            last_op_result_.success_count++;
        } else {
            last_op_result_.not_found_count++;
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

// --- 数据获取方法现在全部委托给 db_manager_ ---

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

// --- 状态获取方法保持不变 ---

AppStatus Application::get_status() const {
    return status_;
}

const OperationResult& Application::get_operation_result() const {
    return last_op_result_;
}