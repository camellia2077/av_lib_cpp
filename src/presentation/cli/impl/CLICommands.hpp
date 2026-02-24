// adapters/cli/impl/CLICommands.hpp
#ifndef CLI_COMMANDS_HPP
#define CLI_COMMANDS_HPP

#include <string>
#include <vector>

#include "core/app/application.hpp"

class CLICommands {
 public:
  explicit CLICommands(Application& app);

  void AddIds(const std::string& input);
  void QueryId(const std::string& input);
  void CreateDatabase(const std::string& name);
  void SwitchDatabase();
  void ImportFromFile(const std::string& filepath);
  void ExportToFile(const std::string& filepath);
  void ShowStatus();
  static void ShowVersion();

 private:
  Application& app_;
};

#endif
