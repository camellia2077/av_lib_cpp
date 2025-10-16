// App/DatabaseManager.cpp
#include "DatabaseManager.hpp"
#include <filesystem>
#include <string>
#include <iostream> // 用于错误输出

// --- 平台相关的头文件，用于获取可执行文件路径 ---
#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#include <limits.h>
#endif

// --- 辅助函数：获取可执行文件所在的目录 ---
namespace {
std::string get_executable_directory() {
    char path[1024];
#ifdef _WIN32
    GetModuleFileNameA(NULL, path, sizeof(path));
#else
    ssize_t count = readlink("/proc/self/exe", path, sizeof(path));
    if (count > 0) path[count] = '\0';
#endif
    return std::filesystem::path(path).parent_path().string();
}
}

DatabaseManager::DatabaseManager() {
    // 1. 获取可执行文件目录，并构建data目录的路径
    data_directory_path_ = get_executable_directory() + "/data";
    
    // 2. 确保这个data目录存在
    ensure_data_directory_exists();
    
    // 3. 设置默认数据库名称 (只是名字，不含路径)
    current_db_name_ = "database.sqlite3";
}

void DatabaseManager::ensure_data_directory_exists() {
    if (!std::filesystem::exists(data_directory_path_)) {
        std::filesystem::create_directory(data_directory_path_);
    }
}

std::string DatabaseManager::get_db_filepath(const std::string& db_name) const {
    return data_directory_path_ + "/" + db_name;
}

void DatabaseManager::load_default_database() {
    std::string full_path = get_db_filepath(current_db_name_);
    dbs_[current_db_name_] = std::make_unique<FastQueryDB>(full_path);
}

bool DatabaseManager::create_database(const std::string& db_name_raw) {
    std::string new_db_name = db_name_raw;
    if (new_db_name.find(".sqlite3") == std::string::npos) {
        new_db_name += ".sqlite3";
    }

    if (database_exists(new_db_name)) {
        return false;
    }

    try {
        std::string full_path = get_db_filepath(new_db_name);
        auto db = std::make_unique<FastQueryDB>(full_path);
        dbs_[new_db_name] = std::move(db);
        current_db_name_ = new_db_name;
        return true;
    } catch (const std::exception& e) {
        std::cerr << "创建数据库失败: " << e.what() << std::endl;
        return false;
    }
}

bool DatabaseManager::switch_to_database(const std::string& db_name) {
    std::string full_path = get_db_filepath(db_name);
    // 如果数据库已在内存中
    if (dbs_.count(db_name)) {
        current_db_name_ = db_name;
        return true;
    }
    // 如果不在内存中，但文件存在，则加载它
    if (std::filesystem::exists(full_path)) {
        try {
            dbs_[db_name] = std::make_unique<FastQueryDB>(full_path);
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
    // 始终检查文件系统中的完整路径
    return std::filesystem::exists(get_db_filepath(db_name));
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
    if (!std::filesystem::exists(data_directory_path_)) {
        return names;
    }
    // 只扫描我们固定的data目录
    for (const auto& entry : std::filesystem::directory_iterator(data_directory_path_)) {
        if (entry.is_regular_file() && entry.path().extension() == ".sqlite3") {
            names.push_back(entry.path().filename().string());
        }
    }
    return names;
}