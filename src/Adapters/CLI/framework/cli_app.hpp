// adapters/cli/framework/cli_app.hpp
#ifndef CLI_APP_HPP
#define CLI_APP_HPP

#include "adapters/cli/impl/CLICommands.hpp"
#include <string>

class CLIApp {
public:
  explicit CLIApp(Application &app);
  void run();

private:
  void clear_screen();
  void print_status_message();
  void print_menu(const std::string &current_db);
  void clear_cin();

  Application &app_;
  CLICommands commands_;
};

#endif
