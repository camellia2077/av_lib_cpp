#pragma once

#include "Data/FastQueryDB.h"
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
    std::map<std::string, std::unique_ptr<FastQueryDB>> dbs_;
    std::string current_db_name_;
};