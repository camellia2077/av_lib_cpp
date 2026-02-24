// infrastructure/database_manager.cpp
#include "core/infrastructure/database_manager.hpp"

#include <filesystem>
#include <iostream>  // 用于错误输出

#include "core/data/fast_query_db.hpp"

// --- 平台相关的头文件，用于获取可执行文件路径 ---
#ifdef _WIN32
#include <windows.h>
#else
#include <limits.h>
#include <unistd.h>
#endif

// --- 辅助函数：获取可执行文件所在的目录 ---
namespace {
auto GetExecutableDirectory() -> std::string {
  char path[1024];
#ifdef _WIN32
  GetModuleFileNameA(nullptr, path, sizeof(path));
#else
  ssize_t count = readlink("/proc/self/exe", path, sizeof(path));
  if (count > 0) path[count] = '\0';
#endif
  return std::filesystem::path(path).parent_path().string();
}
}  // namespace

DatabaseManager::DatabaseManager() {
  // 1. 获取可执行文件目录，并构建data目录的路径
  data_directory_path_ = GetExecutableDirectory() + "/data";

  // 2. 确保这个data目录存在
  EnsureDataDirectoryExists();

  // 3. 设置默认数据库名称 (只是名字，不含路径)
  current_db_name_ = "database.sqlite3";
}

void DatabaseManager::EnsureDataDirectoryExists() {
  if (!std::filesystem::exists(data_directory_path_)) {
    std::filesystem::create_directory(data_directory_path_);
  }
}

auto DatabaseManager::GetDbFilepath(const std::string& db_name) const
    -> std::string {
  return data_directory_path_ + "/" + db_name;
}

void DatabaseManager::LoadDefaultDatabase() {
  std::string full_path = GetDbFilepath(current_db_name_);
  dbs_[current_db_name_] = std::make_unique<FastQueryDB>(full_path);
}

auto DatabaseManager::CreateDatabase(const std::string& db_name_raw) -> bool {
  std::string new_db_name = db_name_raw;
  if (new_db_name.find(".sqlite3") == std::string::npos) {
    new_db_name += ".sqlite3";
  }

  if (DatabaseExists(new_db_name)) {
    return false;
  }

  try {
    std::string full_path = GetDbFilepath(new_db_name);
    auto db = std::make_unique<FastQueryDB>(full_path);
    dbs_[new_db_name] = std::move(db);
    current_db_name_ = new_db_name;
    return true;
  } catch (const std::exception& e) {
    std::cerr << "创建数据库失败: " << e.what() << std::endl;
    return false;
  }
}

auto DatabaseManager::SwitchToDatabase(const std::string& db_name) -> bool {
  std::string full_path = GetDbFilepath(db_name);
  if (dbs_.contains(db_name) != 0u) {
    current_db_name_ = db_name;
    return true;
  }
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

auto DatabaseManager::DatabaseExists(const std::string& db_name) const -> bool {
  return std::filesystem::exists(GetDbFilepath(db_name));
}

auto DatabaseManager::GetCurrentDb() const -> IIdRepository* {
  if (dbs_.contains(current_db_name_) != 0u) {
    return dbs_.at(current_db_name_).get();
  }
  return nullptr;
}

auto DatabaseManager::GetCurrentDbName() const -> const std::string& {
  return current_db_name_;
}

auto DatabaseManager::GetAllDbNames() const -> std::vector<std::string> {
  std::vector<std::string> names;
  if (!std::filesystem::exists(data_directory_path_)) {
    return names;
  }
  for (const auto& entry :
       std::filesystem::directory_iterator(data_directory_path_)) {
    if (entry.is_regular_file() && entry.path().extension() == ".sqlite3") {
      names.push_back(entry.path().filename().string());
    }
  }
  return names;
}
