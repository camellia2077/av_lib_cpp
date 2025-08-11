#pragma once

#include "DatabaseManager.h" // 包含新的管理器
#include <string>
#include <memory>
#include <vector>

// AppStatus 和 OperationResult 定义保持不变
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
    ErrorIdInvalid,
};

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

    // --- 业务逻辑方法 (委托给DatabaseManager或使用它) ---
    void load_database();
    void perform_add(const std::string& input);
    void perform_query(const std::string& input);
    void perform_create_database(const std::string& new_db_name);
    void set_current_database(const std::string& db_name);

    // --- 状态获取方法 ---
    AppStatus get_status() const;
    const OperationResult& get_operation_result() const;
    
    // --- 数据获取 (直接从管理器获取) ---
    size_t get_total_records() const;
    std::vector<std::string> get_database_names() const;
    const std::string& get_current_db_name() const;

private:
    // 关键修改：拥有一个数据库管理器实例
    std::unique_ptr<DatabaseManager> db_manager_;

    // 应用自身的状态
    AppStatus status_; 
    OperationResult last_op_result_;
};