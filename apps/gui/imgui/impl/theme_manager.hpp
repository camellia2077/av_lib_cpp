// apps/gui/imgui/impl/theme_manager.hpp
#ifndef THEME_MANAGER_HPP
#define THEME_MANAGER_HPP

#include "imgui.h"

// 将主题相关的实现细节封装起来
class ThemeManager {
 public:
  ThemeManager();

  // 应用一个主题
  void ApplyTheme(int theme_index);

  // 设置圆角风格
  static void SetupRoundedStyle();

  // 获取当前主题的索引
  auto GetCurrentThemeIndex() -> int& { return current_theme_index_; }

 private:
  static constexpr int kThemeLight = 1;
  int current_theme_index_{kThemeLight};
};

#endif  // THEME_MANAGER_HPP

