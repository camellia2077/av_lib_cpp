// adapters/cli/framework/cli_app.hpp
#ifndef CLI_APP_HPP
#define CLI_APP_HPP

#include <string>

#include "presentation/cli/impl/CLICommands.hpp"

class CLIApp {
 public:
  explicit CLIApp(Application& app);
  void Run();

 private:
  static void clear_screen();
  void print_status_message();
  static void print_menu(const std::string& current_db);
  static void clear_cin();

  Application& app_;
  CLICommands commands_;
};

#endif
