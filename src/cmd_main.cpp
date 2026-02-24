// cmd_main.cpp
#include <memory>

#include "presentation/cli/framework/cli_app.hpp"
#include "core/app/application.hpp"
#include "core/infrastructure/database_manager.hpp"

int main() {
  Application app(std::make_unique<DatabaseManager>());
  CLIApp cli(app);
  cli.Run();
  return 0;
}
