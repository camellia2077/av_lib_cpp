// view/imgui/impl/im_gui_view.hpp
#ifndef IM_GUI_VIEW_HPP
#define IM_GUI_VIEW_HPP

#include "view/i_gui_view.hpp"
#include "view/imgui/impl/imgui_settings_store.hpp"
#include "view/imgui/impl/theme_manager.hpp"
#include "view/imgui/impl/ui_panel.hpp"
#include <memory>

struct GLFWwindow;

class ImGuiView : public IGuiView {
public:
  explicit ImGuiView(Application &app);
  ~ImGuiView() override = default;

  bool init() override;
  void run() override;
  void cleanup() override;

private:
  void render_frame();

  Application &app_;
  GLFWwindow *window_;

  std::unique_ptr<ThemeManager> theme_manager_;
  std::unique_ptr<ImGuiSettingsStore> settings_store_;
  std::unique_ptr<UIPanel> ui_panel_;
};

#endif // IM_GUI_VIEW_HPP
