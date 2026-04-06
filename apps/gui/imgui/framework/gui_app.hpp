// apps/gui/imgui/framework/gui_app.hpp
#ifndef GUI_APP_HPP
#define GUI_APP_HPP

#include <memory>

#include "apps/gui/i_gui_view.hpp"

class GuiApp {
 public:
  explicit GuiApp(std::unique_ptr<IGuiView> view);
  void Run();

 private:
  std::unique_ptr<IGuiView> view_;
};

#endif

