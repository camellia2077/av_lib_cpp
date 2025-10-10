// App/Application.hpp
#ifndef APPLICATION_HPP
#define APPLICATION_HPP

#include "DatabaseManager.hpp"
#include <string>
#include <memory>
#include <vector>

enum class AppStatus {
    Idle,
    Welcome,
    DBLoadSuccess,
    DBSwitched,
    DBCreated,
    AddCompleted,
    QueryCompleted,
    ImportCompleted,
    ErrorDBNotExist,
    ErrorDBCreateFailed,
    ErrorDBNameExists,
    ErrorDBNameEmpty,
    ErrorAddIDEmpty,
    ErrorQueryIDEmpty,
    ErrorIdInvalid,
    ErrorFileOpenFailed,
    ErrorFileEmpty,
};

// (struct OperationResult remains the same)
struct OperationResult {
    size_t success_count = 0;
    size_t exist_count = 0;
    size_t not_found_count = 0;
    size_t invalid_format_count = 0;
    std::string target_db_name;
};


class Application {
public:
    Application();

    // --- Business Logic ---
    void load_database();
    void perform_add(const std::string& input);
    void perform_query(const std::string& input);
    void perform_create_database(const std::string& new_db_name);
    void set_current_database(const std::string& db_name);
    void perform_import_from_file(const std::string& filepath);

    // --- Status Getters and Setters ---
    AppStatus get_status() const;
    const OperationResult& get_operation_result() const;
    void set_status(AppStatus new_status);
    
    // --- Data Getters ---
    size_t get_total_records() const;
    std::vector<std::string> get_database_names() const;
    const std::string& get_current_db_name() const;

private:
    std::unique_ptr<DatabaseManager> db_manager_;
    AppStatus status_; 
    OperationResult last_op_result_;
};
#endif