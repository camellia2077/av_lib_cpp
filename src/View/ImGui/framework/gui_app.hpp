// view/imgui/framework/gui_app.hpp
#ifndef GUI_APP_HPP
#define GUI_APP_HPP

#include "view/i_gui_view.hpp"
#include <memory>

class GuiApp {
public:
  explicit GuiApp(std::unique_ptr<IGuiView> view);
  void run();

private:
  std::unique_ptr<IGuiView> view_;
};

#endif
