#include "Application.h"
#include "UIText.h" // <-- 新增：包含我们新的文本头文件
#include <cstring> 

Application::Application() {
    db_ = std::make_unique<FastQueryDB>("database.bin");
    add_buffer_[0] = '\0';
    query_buffer_[0] = '\0';
    // 使用新的文本常量来初始化状态消息
    status_message_ = UIText::Welcome;
    total_records_ = 0;
}

void Application::load_database() {
    db_->load();
    total_records_ = db_->get_count();
    status_message_ = UIText::DBLoadSuccess;
}

void Application::perform_add() {
    std::string id_to_add = add_buffer_;
    if (id_to_add.empty()) {
        status_message_ = UIText::ErrorAddEmptyID;
        return;
    }
    
    if (db_->add(id_to_add)) {
        // 构造动态字符串
        status_message_ = std::string(UIText::InfoAddSuccess) + id_to_add;
        add_buffer_[0] = '\0'; // 清空缓冲区
        total_records_ = db_->get_count(); // 更新总数
    } else {
        status_message_ = std::string(UIText::ErrorIDExistsPart1) + id_to_add + std::string(UIText::ErrorIDExistsPart2);
    }
}

void Application::perform_query() {
    std::string id_to_query = query_buffer_;
     if (id_to_query.empty()) {
        status_message_ = UIText::InfoQueryPrompt;
        return;
    }

    if (db_->exists(id_to_query)) {
        status_message_ = std::string(UIText::ResultIDFoundPart1) + id_to_query + std::string(UIText::ResultIDFoundPart2);
    } else {
        status_message_ = std::string(UIText::ResultIDNotFoundPart1) + id_to_query + std::string(UIText::ResultIDNotFoundPart2);
    }
}

const char* Application::get_add_buffer() const { return add_buffer_; }
void Application::set_add_buffer(const char* text) { strncpy(add_buffer_, text, sizeof(add_buffer_) - 1); }

const char* Application::get_query_buffer() const { return query_buffer_; }
void Application::set_query_buffer(const char* text) { strncpy(query_buffer_, text, sizeof(query_buffer_) - 1); }

const std::string& Application::get_status_message() const { return status_message_; }
size_t Application::get_total_records() const { return total_records_; }