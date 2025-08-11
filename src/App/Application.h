#pragma once

#include "Data/FastQueryDB.h"
#include <string>
#include <memory>
#include <vector>
#include <map>

// 新增：定义应用可能出现的各种状态，供UI层查询并翻译成对应文本
enum class AppStatus {
    Idle,
    Welcome,
    DBLoadSuccess,
    DBSwitched,
    DBCreated,
    AddCompleted,
    QueryCompleted,
    ErrorDBNotExist,
    ErrorDBCreateFailed,
    ErrorDBNameExists,
    ErrorDBNameEmpty,
    ErrorAddIDEmpty,
    ErrorQueryIDEmpty,
    ErrorIdInvalid, // 代表批量操作中至少有一个ID格式无效
};

// 新增：用于存储批量操作结果的结构体
struct OperationResult {
    size_t success_count = 0;
    size_t exist_count = 0;
    size_t not_found_count = 0;
    size_t invalid_format_count = 0;
    std::string target_db_name;
};

// 应用逻辑层
class Application {
public:
    Application();

    // --- 业务逻辑方法 ---
    // 输入参数从读取内部buffer改为了直接传递
    void load_database();
    void perform_add(const std::string& input);
    void perform_query(const std::string& input);
    void perform_create_database(const std::string& new_db_name);
    void set_current_database(const std::string& db_name);

    // --- 状态获取方法 ---
    // get_status_message 被 get_status 和 get_operation_result 取代
    AppStatus get_status() const;
    const OperationResult& get_operation_result() const;
    
    size_t get_total_records() const;
    std::vector<std::string> get_database_names() const;
    const std::string& get_current_db_name() const;

private:
    std::map<std::string, std::unique_ptr<FastQueryDB>> dbs_;
    std::string current_db_name_;

    // --- 应用状态 ---
    // 不再存储UI字符串，而是存储状态码和结构化数据
    AppStatus status_; 
    OperationResult last_op_result_;
};