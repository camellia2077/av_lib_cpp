#include "common/pch.h"
#include "Application.h"
#include "View/ImGui/UIConfig.h" // <-- 主要修改点：替换头文件
#include "Utils/Validator.h"
#include <cstring>
#include <vector>
#include <sstream>
#include <filesystem>

namespace fs = std::filesystem;

Application::Application() {
    // 默认数据库
    current_db_name_ = "database.bin";
    
    add_buffer_[0] = '\0';
    query_buffer_[0] = '\0';
    new_db_name_buffer_[0] = '\0';
    status_message_ = UIConfig::Welcome; // 现在可以正确找到
    total_records_ = 0;
}

void Application::load_database() {
    // 加载默认数据库
    dbs_[current_db_name_] = std::make_unique<FastQueryDB>(current_db_name_);
    dbs_[current_db_name_]->load();
    
    total_records_ = dbs_[current_db_name_]->get_count();
    status_message_ = UIConfig::DBLoadSuccess; // 现在可以正确找到
}

// --- 新增的创建数据库函数 ---
void Application::perform_create_database() {
    std::string new_db_name = new_db_name_buffer_;
    if (new_db_name.empty()) {
        status_message_ = "错误: 新数据库名称不能为空。";
        return;
    }

    // 确保文件名以 .bin 结尾
    if (new_db_name.rfind(".bin") == std::string::npos) {
        new_db_name += ".bin";
    }

    // 检查数据库是否已存在
    if (dbs_.count(new_db_name)) {
        status_message_ = "错误: 数据库 '" + new_db_name + "' 已存在。";
        return;
    }

    // 创建实例并保存一个空的数据库文件
    dbs_[new_db_name] = std::make_unique<FastQueryDB>(new_db_name);
    if (dbs_[new_db_name]->save()) { // 调用save()来创建物理文件
        status_message_ = "成功创建数据库: " + new_db_name;
        current_db_name_ = new_db_name; // 自动切换到新创建的库
        new_db_name_buffer_[0] = '\0'; // 清空输入框
        total_records_ = 0;
    } else {
        status_message_ = "错误: 创建数据库文件失败。";
        dbs_.erase(new_db_name); // 创建失败，从map中移除
    }
}

// --- 简化后的添加函数 ---
void Application::perform_add() {
    const std::string& target_db = current_db_name_;

    if (dbs_.find(target_db) == dbs_.end()) {
        status_message_ = "错误: 未选择有效的数据库。";
        return;
    }
    
    std::string full_input = add_buffer_;
    if (full_input.empty()) {
        status_message_ = UIConfig::ErrorAddEmptyID; // 现在可以正确找到
        return;
    }

    std::stringstream ss(full_input);
    std::string id;
    std::vector<std::string> added_ids, existing_ids, invalid_ids;

    while (ss >> id) {
        if (!Validator::isValidIDFormat(id)) {
            invalid_ids.push_back(id);
        } else if (dbs_[target_db]->add(id)) {
            added_ids.push_back(id);
        } else {
            existing_ids.push_back(id);
        }
    }

    std::stringstream result_ss;
    result_ss << "在 [" << target_db << "] 处理完成. ";
    result_ss << "成功添加: " << added_ids.size() << "个. ";
    if (!existing_ids.empty()) {
        result_ss << "已存在: " << existing_ids.size() << "个. ";
    }
    if (!invalid_ids.empty()) {
        result_ss << "格式错误: " << invalid_ids.size() << "个.";
    }
    status_message_ = result_ss.str();

    if (!added_ids.empty()) {
        add_buffer_[0] = '\0';
        total_records_ = dbs_[target_db]->get_count();
    }
}

void Application::perform_query() {
    if (dbs_.find(current_db_name_) == dbs_.end()) {
        status_message_ = "错误: 未选择任何数据库!";
        return;
    }

    std::string full_input = query_buffer_;
     if (full_input.empty()) {
        status_message_ = UIConfig::InfoQueryPrompt; // 现在可以正确找到
        return;
    }

    std::stringstream ss(full_input);
    std::string id;
    std::vector<std::string> found_ids, not_found_ids, invalid_ids;

    while (ss >> id) {
        if (!Validator::isValidIDFormat(id)) {
            invalid_ids.push_back(id);
        } else if (dbs_[current_db_name_]->exists(id)) {
            found_ids.push_back(id);
        } else {
            not_found_ids.push_back(id);
        }
    }

    std::stringstream result_ss;
    result_ss << "在 [" << current_db_name_ << "] 查询完成. ";
    result_ss << "找到: " << found_ids.size() << "个. ";
    result_ss << "未找到: " << not_found_ids.size() << "个. ";
    if (!invalid_ids.empty()) {
        result_ss << "格式错误: " << invalid_ids.size() << "个.";
    }
    status_message_ = result_ss.str();
}

void Application::set_current_database(const std::string& db_name) {
    if (dbs_.count(db_name)) {
        current_db_name_ = db_name;
        total_records_ = dbs_[current_db_name_]->get_count();
        status_message_ = "已切换到数据库: " + db_name;
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

const char* Application::get_add_buffer() const { return add_buffer_; }
void Application::set_add_buffer(const char* text) { strncpy(add_buffer_, text, sizeof(add_buffer_) - 1); }

const char* Application::get_query_buffer() const { return query_buffer_; }
void Application::set_query_buffer(const char* text) { strncpy(query_buffer_, text, sizeof(query_buffer_) - 1); }

const char* Application::get_new_db_name_buffer() const { return new_db_name_buffer_; }
void Application::set_new_db_name_buffer(const char* text) { strncpy(new_db_name_buffer_, text, sizeof(new_db_name_buffer_) - 1); }

const std::string& Application::get_status_message() const { return status_message_; }
size_t Application::get_total_records() const {
    if (dbs_.count(current_db_name_)) {
        return dbs_.at(current_db_name_)->get_count();
    }
    return 0;
}