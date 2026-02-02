// adapters/cli/impl/CLICommands.hpp
#ifndef CLI_COMMANDS_HPP
#define CLI_COMMANDS_HPP

#include "app/application.hpp"
#include <string>
#include <vector>

class CLICommands {
public:
  explicit CLICommands(Application &app);

  void add_ids(const std::string &input);
  void query_id(const std::string &input);
  void create_database(const std::string &name);
  void switch_database();
  void import_from_file(const std::string &filepath);
  void export_to_file(const std::string &filepath);
  void show_status();
  void show_version();

private:
  Application &app_;
};

#endif
