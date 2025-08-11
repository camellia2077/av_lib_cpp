#include "Application.h"
// #include "View/ImGui/UIConfig.h" // <-- 关键修改：已移除对UI头文件的依赖
#include "Utils/Validator.h"
#include <cstring>
#include <vector>
#include <sstream>
#include <filesystem>

Application::Application() 
    : status_(AppStatus::Welcome) // 初始化状态
{
    // 默认数据库
    current_db_name_ = "database.bin";
}

void Application::load_database() {
    // 确保目录存在
    // (此处可以添加创建目录的逻辑，如果需要)

    // 加载默认数据库
    dbs_[current_db_name_] = std::make_unique<FastQueryDB>(current_db_name_);
    dbs_[current_db_name_]->load();
    
    status_ = AppStatus::DBLoadSuccess;
}

void Application::perform_create_database(const std::string& new_db_name_raw) {
    if (new_db_name_raw.empty()) {
        status_ = AppStatus::ErrorDBNameEmpty;
        return;
    }
    
    std::string new_db_name = new_db_name_raw;
    // 确保文件名以 .bin 结尾
    if (new_db_name.rfind(".bin") == std::string::npos) {
        new_db_name += ".bin";
    }

    if (dbs_.count(new_db_name)) {
        status_ = AppStatus::ErrorDBNameExists;
        return;
    }

    dbs_[new_db_name] = std::make_unique<FastQueryDB>(new_db_name);
    if (dbs_[new_db_name]->save()) {
        current_db_name_ = new_db_name;
        status_ = AppStatus::DBCreated;
    } else {
        dbs_.erase(new_db_name);
        status_ = AppStatus::ErrorDBCreateFailed;
    }
}

void Application::perform_add(const std::string& input) {
    if (dbs_.find(current_db_name_) == dbs_.end()) {
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
    last_op_result_.target_db_name = current_db_name_;

    while (ss >> id) {
        if (!Validator::isValidIDFormat(id)) {
            last_op_result_.invalid_format_count++;
        } else if (dbs_[current_db_name_]->add(id)) {
            last_op_result_.success_count++;
        } else {
            last_op_result_.exist_count++;
        }
    }

    status_ = AppStatus::AddCompleted;
}

void Application::perform_query(const std::string& input) {
    if (dbs_.find(current_db_name_) == dbs_.end()) {
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
    last_op_result_.target_db_name = current_db_name_;

    while (ss >> id) {
        if (!Validator::isValidIDFormat(id)) {
            last_op_result_.invalid_format_count++;
        } else if (dbs_[current_db_name_]->exists(id)) {
            last_op_result_.success_count++;
        } else {
            last_op_result_.not_found_count++;
        }
    }
    
    status_ = AppStatus::QueryCompleted;
}

void Application::set_current_database(const std::string& db_name) {
    if (dbs_.count(db_name)) {
        current_db_name_ = db_name;
        status_ = AppStatus::DBSwitched;
    } else {
        status_ = AppStatus::ErrorDBNotExist;
    }
}

std::vector<std::string> Application::get_database_names() const {
    std::vector<std::string> names;
    for(const auto& pair : dbs_) {
        names.push_back(pair.first);
    }
    return names;
}

const std::string& Application::get_current_db_name() const {
    return current_db_name_;
}

AppStatus Application::get_status() const {
    return status_;
}

const OperationResult& Application::get_operation_result() const {
    return last_op_result_;
}

size_t Application::get_total_records() const {
    if (dbs_.count(current_db_name_)) {
        return dbs_.at(current_db_name_)->get_count();
    }
    return 0;
}