// main.cpp

#include <memory>

#include "core/app/application.hpp"
#include "core/infrastructure/database_manager.hpp"
#include "apps/gui/imgui/framework/gui_app.hpp"
#include "apps/gui/imgui/impl/im_gui_view.hpp"

auto main(int /*unused*/, char** /*unused*/) -> int {
  // 1. 创建应用逻辑层实例
  Application app(std::make_unique<DatabaseManager>());

  // 2. 创建一个GUI视图的实现，并把App的引用传给它
  //    如果想换成Qt，只需要改成 std::make_unique<QtView>(app)
  std::unique_ptr<IGuiView> gui = std::make_unique<ImGuiView>(app);
  GuiApp gui_app(std::move(gui));

  // 3. 启动GUI
  gui_app.Run();

  return 0;
}

