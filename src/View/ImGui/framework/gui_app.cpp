// view/imgui/framework/gui_app.cpp
#include "view/imgui/framework/gui_app.hpp"

GuiApp::GuiApp(std::unique_ptr<IGuiView> view) : view_(std::move(view)) {}

void GuiApp::run() {
  if (view_ && view_->init()) {
    view_->run();
  }
  if (view_) {
    view_->cleanup();
  }
}
