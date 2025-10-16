// App/DatabaseManager.hpp
#ifndef DATABASE_MANAGER_HPP
#define DATABASE_MANAGER_HPP

#include "Data/FastQueryDB.hpp"
#include <string>
#include <vector>
#include <memory>
#include <map>

class DatabaseManager {
public:
    DatabaseManager();

    // --- 数据库生命周期管理 ---
    void load_default_database();
    bool create_database(const std::string& db_name_raw);
    bool switch_to_database(const std::string& db_name);
    bool database_exists(const std::string& db_name) const;

    // --- 数据访问 ---
    FastQueryDB* get_current_db() const;
    const std::string& get_current_db_name() const;
    std::vector<std::string> get_all_db_names() const;

private:
    void ensure_data_directory_exists(); // 确保数据目录存在
    std::string get_db_filepath(const std::string& db_name) const; // 获取数据库文件的完整路径

    std::map<std::string, std::unique_ptr<FastQueryDB>> dbs_;
    std::string current_db_name_;
    std::string data_directory_path_; // 保存数据目录的路径
};
#endif