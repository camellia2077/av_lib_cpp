// App/DatabaseManager.cpp
#include "DatabaseManager.hpp"
#include <filesystem>
#include <string>

DatabaseManager::DatabaseManager() {
    // 默认数据库名称更改为 .sqlite3
    current_db_name_ = "database.sqlite3";
}

void DatabaseManager::load_default_database() {
    dbs_[current_db_name_] = std::make_unique<FastQueryDB>(current_db_name_);
}

bool DatabaseManager::create_database(const std::string& db_name_raw) {
    std::string new_db_name = db_name_raw;

    // 确保文件名以 .sqlite3 结尾
    if (new_db_name.find(".sqlite3") == std::string::npos) {
        new_db_name += ".sqlite3";
    }

    if (dbs_.count(new_db_name)) {
        return false; // 数据库已存在
    }

    try {
        // 构造 FastQueryDB 会自动创建文件
        auto db = std::make_unique<FastQueryDB>(new_db_name);
        dbs_[new_db_name] = std::move(db);
        current_db_name_ = new_db_name;
        return true;
    } catch (const std::exception& e) {
        // 如果创建失败 (例如，没有写权限)，则捕获异常
        std::cerr << "创建数据库失败: " << e.what() << std::endl;
        return false;
    }
}

bool DatabaseManager::switch_to_database(const std::string& db_name) {
    if (dbs_.count(db_name)) {
        current_db_name_ = db_name;
        return true;
    }
    // 如果数据库不在内存中，但文件存在，则加载它
    if (std::filesystem::exists(db_name)) {
        try {
            dbs_[db_name] = std::make_unique<FastQueryDB>(db_name);
            current_db_name_ = db_name;
            return true;
        } catch (const std::exception& e) {
            std::cerr << "切换并加载数据库失败: " << e.what() << std::endl;
            return false;
        }
    }
    return false;
}

bool DatabaseManager::database_exists(const std::string& db_name) const {
    if (dbs_.count(db_name) > 0) {
        return true;
    }
    // 同时检查文件系统
    return std::filesystem::exists(db_name);
}

FastQueryDB* DatabaseManager::get_current_db() const {
    if (dbs_.count(current_db_name_)) {
        return dbs_.at(current_db_name_).get();
    }
    return nullptr;
}

const std::string& DatabaseManager::get_current_db_name() const {
    return current_db_name_;
}

std::vector<std::string> DatabaseManager::get_all_db_names() const {
    std::vector<std::string> names;
    // 除了内存中的，也扫描当前目录下的 .sqlite3 文件
    std::filesystem::path current_path(".");
    for (const auto& entry : std::filesystem::directory_iterator(current_path)) {
        if (entry.is_regular_file() && entry.path().extension() == ".sqlite3") {
            names.push_back(entry.path().filename().string());
        }
    }
    // 去重
    std::sort(names.begin(), names.end());
    names.erase(std::unique(names.begin(), names.end()), names.end());
    return names;
}