#pragma once

#include "Data/FastQueryDB.h"
#include <string>
#include <memory>

// 应用逻辑层
class Application {
public:
    Application();

    // -- 提供给GUI调用的业务逻辑方法 --
    void load_database();
    void perform_add();
    void perform_query();

    // -- 提供给GUI获取和设置状态的方法 --
    // 使用指针以避免不必要的字符串拷贝
    const char* get_add_buffer() const;
    void set_add_buffer(const char* text);

    const char* get_query_buffer() const;
    void set_query_buffer(const char* text);
    
    const std::string& get_status_message() const;
    size_t get_total_records() const;

private:
    std::unique_ptr<FastQueryDB> db_;

    // 应用状态，GUI将从这里读取数据来渲染
    char add_buffer_[128];
    char query_buffer_[128];
    std::string status_message_;
    size_t total_records_;
};