// apps/cli/impl/CLICommands.cpp
#include "apps/cli/impl/CLICommands.hpp"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <utility>

#include "apps/cli/input_parser.hpp"
#include "common/version.hpp"
#include "core/io/text_file_reader.hpp"

CLICommands::CLICommands(Application& app) : app_(app) {}

void CLICommands::AddIds(const std::string& input) {
  app_.PerformAdd(Adapters::SplitIds(input));
}

void CLICommands::QueryId(const std::string& input) {
  app_.PerformQuery(input);
}

void CLICommands::CreateDatabase(const std::string& name) {
  app_.PerformCreateDatabase(name);
}

void CLICommands::SwitchDatabase() {
  std::vector<std::string> dbs = app_.GetDatabaseNames();
  if (dbs.empty()) {
    std::cout << "当前没有可切换的数据库。" << std::endl;
    return;
  }
  std::cout << "可用数据库:" << std::endl;
  for (size_t i = 0; i < dbs.size(); ++i) {
    std::cout << i + 1 << ". " << dbs[i] << std::endl;
  }
  std::cout << "选择要切换的数据库编号: ";
  int db_choice;
  std::cin >> db_choice;
  if (std::cin.fail() || db_choice < 1 ||
      std::cmp_greater(db_choice, dbs.size())) {
    app_.SetError(ErrorCode::kIdInvalid);
    std::cin.clear();
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    return;
  }
  std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
  app_.SetCurrentDatabase(dbs[db_choice - 1]);
}

void CLICommands::ImportFromFile(const std::string& filepath) {
  try {
    IO::TextFileReader reader;
    auto lines = reader.ReadAllLines(filepath);
    app_.PerformImportLines(lines);
  } catch (const std::runtime_error&) {
    app_.SetError(ErrorCode::kFileOpenFailed);
  }
}

void CLICommands::ExportToFile(const std::string& filepath) {
  std::string out_path = filepath;
  if (out_path.empty()) {
    out_path = (std::filesystem::current_path() / "output.txt").string();
  }
  std::vector<std::string> ids;
  if (!app_.FetchAllIds(ids)) {
    return;
  }
  std::ofstream out(out_path, std::ios::out | std::ios::trunc);
  if (!out.is_open()) {
    app_.SetError(ErrorCode::kFileOpenFailed);
    return;
  }
  for (const auto& id : ids) {
    out << id << '\n';
  }
  app_.SetInfoMessage("导出完成，文件路径: " + out_path);
}

void CLICommands::ShowStatus() {
  std::cout << "当前库记录总数: " << app_.GetTotalRecords() << std::endl;
  std::cout << "\n按回车键返回菜单...";
  std::cin.get();
}

void CLICommands::ShowVersion() {
  std::cout << "当前软件版本: " << AppVersion::kVersionString << std::endl;
  std::cout << "\n按回车键返回菜单...";
  std::cin.get();
}

