// main.cpp

#include "app/application.hpp"
#include "infrastructure/database_manager.hpp"
#include "view/imgui/framework/gui_app.hpp"
#include "view/imgui/impl/im_gui_view.hpp"
#include <memory>

int main(int, char **) {
  // 1. 创建应用逻辑层实例
  Application app(std::make_unique<database_manager>());

  // 2. 创建一个GUI视图的实现，并把App的引用传给它
  //    如果想换成Qt，只需要改成 std::make_unique<QtView>(app)
  std::unique_ptr<IGuiView> gui = std::make_unique<ImGuiView>(app);
  GuiApp gui_app(std::move(gui));

  // 3. 启动GUI
  gui_app.run();

  return 0;
}
