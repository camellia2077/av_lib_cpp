// adapters/cli/impl/CLICommands.cpp
#include "CLICommands.hpp"
#include "adapters/input_parser.hpp"
#include "common/version.hpp"
#include "io/text_file_reader.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>

CLICommands::CLICommands(Application &app) : app_(app) {}

void CLICommands::add_ids(const std::string &input) {
  app_.perform_add(Adapters::split_ids(input));
}

void CLICommands::query_id(const std::string &input) {
  app_.perform_query(input);
}

void CLICommands::create_database(const std::string &name) {
  app_.perform_create_database(name);
}

void CLICommands::switch_database() {
  std::vector<std::string> dbs = app_.get_database_names();
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
      db_choice > static_cast<int>(dbs.size())) {
    app_.set_error(ErrorCode::IdInvalid);
    std::cin.clear();
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    return;
  }
  std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
  app_.set_current_database(dbs[db_choice - 1]);
}

void CLICommands::import_from_file(const std::string &filepath) {
  try {
    IO::TextFileReader reader;
    auto lines = reader.read_all_lines(filepath);
    app_.perform_import_lines(lines);
  } catch (const FileOpenException &) {
    app_.set_error(ErrorCode::FileOpenFailed);
  }
}

void CLICommands::export_to_file(const std::string &filepath) {
  std::string out_path = filepath;
  if (out_path.empty()) {
    out_path = (std::filesystem::current_path() / "output.txt").string();
  }
  std::vector<std::string> ids;
  if (!app_.fetch_all_ids(ids)) {
    return;
  }
  std::ofstream out(out_path, std::ios::out | std::ios::trunc);
  if (!out.is_open()) {
    app_.set_error(ErrorCode::FileOpenFailed);
    return;
  }
  for (const auto &id : ids) {
    out << id << '\n';
  }
  app_.set_info_message("导出完成，文件路径: " + out_path);
}

void CLICommands::show_status() {
  std::cout << "当前库记录总数: " << app_.get_total_records() << std::endl;
  std::cout << "\n按回车键返回菜单...";
  std::cin.get();
}

void CLICommands::show_version() {
  std::cout << "当前软件版本: " << AppVersion::VersionString << std::endl;
  std::cout << "\n按回车键返回菜单...";
  std::cin.get();
}
