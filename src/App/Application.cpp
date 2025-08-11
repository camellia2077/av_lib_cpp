
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
    
    // 检查时应附加.bin后缀
    std::string db_file_name = new_db_name;
    if (db_file_name.rfind(".bin") == std::string::npos) {
        db_file_name += ".bin";
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

// --- 主要修改区域 ---
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

    // 重置操作结果
    last_op_result_ = {}; 
    last_op_result_.target_db_name = db_manager_->get_current_db_name();

    // 将整个输入视为一个ID进行处理，不再按空格分割
    if (!Validator::isValidIDFormat(input)) {
        last_op_result_.invalid_format_count = 1;
    } else if (current_db->add(input)) {
        last_op_result_.success_count = 1;
    } else {
        last_op_result_.exist_count = 1;
    }

    status_ = AppStatus::AddCompleted;
}

// --- 主要修改区域 ---
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
    
    // 重置操作结果
    last_op_result_ = {};
    last_op_result_.target_db_name = db_manager_->get_current_db_name();

    // 将整个输入视为一个ID进行处理
    if (!Validator::isValidIDFormat(input)) {
        last_op_result_.invalid_format_count = 1;
    } else if (current_db->exists(input)) {
        last_op_result_.success_count = 1;
    } else {
        last_op_result_.not_found_count = 1;
    }
    
    status_ = AppStatus::QueryCompleted;
}
// --- 修改结束 ---

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