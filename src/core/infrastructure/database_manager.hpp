// core/infrastructure/database_manager.hpp
#ifndef DATABASE_MANAGER_HPP
#define DATABASE_MANAGER_HPP

#include <map>
#include <memory>
#include <string>
#include <vector>

#include "core/ports/i_database_catalog.hpp"

class DatabaseManager : public IDatabaseCatalog {
 public:
  DatabaseManager();

  // --- 数据库生命周期管理 ---
  void LoadDefaultDatabase() override;
  auto CreateDatabase(const std::string& db_name_raw) -> bool override;
  auto SwitchToDatabase(const std::string& db_name) -> bool override;
  [[nodiscard]] auto DatabaseExists(const std::string& db_name) const
      -> bool override;

  // --- 数据访问 ---
  [[nodiscard]] auto GetCurrentDb() const -> IIdRepository* override;
  [[nodiscard]] auto GetCurrentDbName() const -> const std::string& override;
  [[nodiscard]] auto GetAllDbNames() const -> std::vector<std::string> override;

 private:
  void EnsureDataDirectoryExists();  // 确保数据目录存在
  [[nodiscard]] auto GetDbFilepath(const std::string& db_name) const
      -> std::string;  // 获取数据库文件的完整路径

  std::map<std::string, std::unique_ptr<IIdRepository>> dbs_;
  std::string current_db_name_;
  std::string data_directory_path_;  // 保存数据目录的路径
};

#endif
