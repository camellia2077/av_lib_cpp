// cmd_main.cpp
#include <memory>

#include "adapters/cli/framework/cli_app.hpp"
#include "app/application.hpp"
#include "infrastructure/database_manager.hpp"

int main() {
  Application app(std::make_unique<DatabaseManager>());
  CLIApp cli(app);
  cli.Run();
  return 0;
}
