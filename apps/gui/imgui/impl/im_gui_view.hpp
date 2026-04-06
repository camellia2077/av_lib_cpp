// apps/gui/imgui/impl/im_gui_view.hpp
#ifndef IM_GUI_VIEW_HPP
#define IM_GUI_VIEW_HPP

#include <memory>

#include "apps/gui/i_gui_view.hpp"
#include "apps/gui/imgui/impl/imgui_settings_store.hpp"
#include "apps/gui/imgui/impl/theme_manager.hpp"
#include "apps/gui/imgui/impl/ui_panel.hpp"

struct GLFWwindow;

class ImGuiView : public IGuiView {
 public:
  explicit ImGuiView(Application& app);
  ~ImGuiView() override = default;

  auto Init() -> bool override;
  void Run() override;
  void Cleanup() override;

 private:
  void RenderFrame();

  Application& app_;
  GLFWwindow* window_{nullptr};

  std::unique_ptr<ThemeManager> theme_manager_;
  std::unique_ptr<ImGuiSettingsStore> settings_store_;
  std::unique_ptr<UIPanel> ui_panel_;
};

#endif  // IM_GUI_VIEW_HPP

