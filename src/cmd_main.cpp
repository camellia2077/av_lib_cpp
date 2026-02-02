// cmd_main.cpp
#include "adapters/cli/framework/cli_app.hpp"
#include "app/application.hpp"
#include "infrastructure/database_manager.hpp"

int main() {
  Application app(std::make_unique<database_manager>());
  CLIApp cli(app);
  cli.run();
  return 0;
}
