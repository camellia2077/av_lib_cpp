#include "common/pch.h"
#include "Application.h"
#include "UIText.h"
#include "Utils/Validator.h" // <-- 包含新的验证模块
#include <cstring>
#include <vector>       // <-- 用于存储处理结果
#include <sstream>      // <-- 用于方便地分割字符串

Application::Application() {
    db_ = std::make_unique<FastQueryDB>("database.bin");
    add_buffer_[0] = '\0';
    query_buffer_[0] = '\0';
    status_message_ = UIText::Welcome;
    total_records_ = 0;
}

void Application::load_database() {
    db_->load();
    total_records_ = db_->get_count();
    status_message_ = UIText::DBLoadSuccess;
}

// --- 以下是重写后的核心逻辑 ---

void Application::perform_add() {
    std::string full_input = add_buffer_;
    if (full_input.empty()) {
        status_message_ = UIText::ErrorAddEmptyID;
        return;
    }

    std::stringstream ss(full_input);
    std::string id;
    std::vector<std::string> added_ids, existing_ids, invalid_ids;

    // 使用 stringstream 按空格分割输入
    while (ss >> id) {
        if (!Validator::isValidIDFormat(id)) {
            invalid_ids.push_back(id);
        } else if (db_->add(id)) {
            added_ids.push_back(id);
        } else {
            existing_ids.push_back(id);
        }
    }

    // 汇总结果并生成状态消息
    std::stringstream result_ss;
    result_ss << "处理完成. ";
    result_ss << "成功添加: " << added_ids.size() << "个. ";
    if (!existing_ids.empty()) {
        result_ss << "已存在: " << existing_ids.size() << "个. ";
    }
    if (!invalid_ids.empty()) {
        result_ss << "格式错误: " << invalid_ids.size() << "个.";
    }
    status_message_ = result_ss.str();

    // 更新记录总数
    if (!added_ids.empty()) {
        add_buffer_[0] = '\0'; // 成功添加后清空输入框
        total_records_ = db_->get_count();
    }
}

void Application::perform_query() {
    std::string full_input = query_buffer_;
     if (full_input.empty()) {
        status_message_ = UIText::InfoQueryPrompt;
        return;
    }

    std::stringstream ss(full_input);
    std::string id;
    std::vector<std::string> found_ids, not_found_ids, invalid_ids;

    while (ss >> id) {
        if (!Validator::isValidIDFormat(id)) {
            invalid_ids.push_back(id);
        } else if (db_->exists(id)) {
            found_ids.push_back(id);
        } else {
            not_found_ids.push_back(id);
        }
    }

    // 汇总结果并生成状态消息
    std::stringstream result_ss;
    result_ss << "查询完成. ";
    result_ss << "找到: " << found_ids.size() << "个. ";
    result_ss << "未找到: " << not_found_ids.size() << "个. ";
    if (!invalid_ids.empty()) {
        result_ss << "格式错误: " << invalid_ids.size() << "个.";
    }
    status_message_ = result_ss.str();
}

// --- 以下函数保持不变 ---

const char* Application::get_add_buffer() const { return add_buffer_; }
void Application::set_add_buffer(const char* text) { strncpy(add_buffer_, text, sizeof(add_buffer_) - 1); }

const char* Application::get_query_buffer() const { return query_buffer_; }
void Application::set_query_buffer(const char* text) { strncpy(query_buffer_, text, sizeof(query_buffer_) - 1); }

const std::string& Application::get_status_message() const { return status_message_; }
size_t Application::get_total_records() const { return total_records_; }