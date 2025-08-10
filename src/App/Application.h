#pragma once

#include "Data/FastQueryDB.h"
#include <string>
#include <memory>
#include <vector>
#include <map>

// 应用逻辑层
class Application {
public:
    Application();

    // -- 提供给GUI调用的业务逻辑方法 --
    void load_database();
    void perform_add();
    void perform_query();
    void set_current_database(const std::string& db_name); // 新增：设置当前数据库
    void perform_create_database(); // <-- 新增：只负责创建数据库的函数

    // -- 提供给GUI获取和设置状态的方法 --
    const char* get_add_buffer() const;
    void set_add_buffer(const char* text);

    const char* get_query_buffer() const;
    void set_query_buffer(const char* text);
    
    // 新增：用于新数据库名称的buffer
    const char* get_new_db_name_buffer() const;
    void set_new_db_name_buffer(const char* text);

    const std::string& get_status_message() const;
    size_t get_total_records() const;
    
    // 新增：获取所有数据库的名称列表，用于下拉菜单
    std::vector<std::string> get_database_names() const;
    const std::string& get_current_db_name() const; // 新增：获取当前数据库名称

private:
    // 将单个数据库实例改为一个从数据库名到实例的映射
    std::map<std::string, std::unique_ptr<FastQueryDB>> dbs_;
    std::string current_db_name_; // 当前选中的数据库名

    // 应用状态，GUI将从这里读取数据来渲染
    char add_buffer_[128];
    char query_buffer_[128];
    char new_db_name_buffer_[128]; // 新增：新数据库名输入框的缓冲区
    std::string status_message_;
    size_t total_records_;
};