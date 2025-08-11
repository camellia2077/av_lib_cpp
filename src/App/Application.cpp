#include "Application.h"
#include "Utils/Validator.h"
#include <vector>
#include <sstream>
#include <filesystem> // 引入 <filesystem>

// --- 新增辅助功能 ---
namespace {
    /**
     * @brief 创建一个规范化的ID字符串。
     * 该函数移除所有非字母和非数字的字符（如空格和连字符）。
     * 它应该在 Validator::isValidIDFormat 返回 true 后被调用。
     * @param raw_id 经过验证的原始ID字符串。
     * @return 一个只包含字母和数字的规范化ID。
     */
    std::string create_canonical_id(const std::string& raw_id) {
        std::string canonical_id;
        canonical_id.reserve(raw_id.length());
        for (char c : raw_id) {
            // 使用从 Validator.h 暴露的辅助函数来筛选字符
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
    
    // --- 修改点：使用 std::filesystem 来处理路径 ---
    std::filesystem::path db_path(new_db_name);
    if (!db_path.has_extension() || db_path.extension() != ".bin") {
        db_path.replace_extension(".bin");
    }
    std::string db_file_name = db_path.string();
    // --- 修改结束 ---

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

    last_op_result_ = {}; 
    last_op_result_.target_db_name = db_manager_->get_current_db_name();

    std::stringstream ss(input);
    std::string id;
    int processed_count = 0;

    while (ss >> id) {
        processed_count++;
        if (!Validator::isValidIDFormat(id)) {
            last_op_result_.invalid_format_count++;
        } else {
            // 关键改动：在添加到数据库前，将ID规范化
            // 例如 "abc-123" 或 "abc 123" 都会变成 "abc123"
            std::string canonical_id = create_canonical_id(id);
            if (current_db->add(canonical_id)) {
                last_op_result_.success_count++;
            } else {
                last_op_result_.exist_count++;
            }
        }
    }
    
    if (processed_count == 0) {
        status_ = AppStatus::ErrorAddIDEmpty;
        return;
    }

    status_ = AppStatus::AddCompleted;
}
// --- 修改结束 ---

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
        // 关键改动：在查询数据库前，将ID规范化
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