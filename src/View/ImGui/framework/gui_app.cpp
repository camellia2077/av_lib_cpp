// view/imgui/framework/gui_app.cpp
#include "view/imgui/framework/gui_app.hpp"

GuiApp::GuiApp(std::unique_ptr<IGuiView> view) : view_(std::move(view)) {}

void GuiApp::Run() {
  if (view_ && view_->Init()) {
    view_->Run();
  }
  if (view_) {
    view_->Cleanup();
  }
}
