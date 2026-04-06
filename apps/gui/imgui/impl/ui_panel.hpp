// apps/gui/imgui/impl/ui_panel.hpp
#ifndef U_I_PANEL_HPP
#define U_I_PANEL_HPP

#include <string>

#include "core/app/application.hpp"
#include "apps/gui/imgui/impl/theme_manager.hpp"  // 包含ThemeManager

class UIPanel {
 public:
  // 构造函数现在接收一个ThemeManager的引用
  explicit UIPanel(Application& app, ThemeManager& theme_manager);

  void Render();

 private:
  void UpdateStatusMessage();

  Application& app_;
  ThemeManager& theme_manager_;  // 保存对ThemeManager的引用

  char add_buffer_[128];
  char query_buffer_[128];
  char new_db_name_buffer_[128];
  char import_path_buffer_[256];
  char export_path_buffer_[256];
  std::string status_message_;
};

#endif  // U_I_PANEL_HPP

