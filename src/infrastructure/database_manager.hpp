// infrastructure/database_manager.hpp
#ifndef DATABASE_MANAGER_HPP
#define DATABASE_MANAGER_HPP

#include "ports/i_database_catalog.hpp"
#include <map>
#include <memory>
#include <string>
#include <vector>

class database_manager : public IDatabaseCatalog {
public:
  database_manager();

  // --- 数据库生命周期管理 ---
  void load_default_database() override;
  bool create_database(const std::string &db_name_raw) override;
  bool switch_to_database(const std::string &db_name) override;
  bool database_exists(const std::string &db_name) const override;

  // --- 数据访问 ---
  IIdRepository *get_current_db() const override;
  const std::string &get_current_db_name() const override;
  std::vector<std::string> get_all_db_names() const override;

private:
  void ensure_data_directory_exists(); // 确保数据目录存在
  std::string
  get_db_filepath(const std::string &db_name) const; // 获取数据库文件的完整路径

  std::map<std::string, std::unique_ptr<IIdRepository>> dbs_;
  std::string current_db_name_;
  std::string data_directory_path_; // 保存数据目录的路径
};

#endif
