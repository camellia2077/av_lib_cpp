// view/imgui/impl/theme_manager.hpp
#ifndef THEME_MANAGER_HPP
#define THEME_MANAGER_HPP

#include "imgui.h"

// 将主题相关的实现细节封装起来
class ThemeManager {
public:
  ThemeManager();

  // 应用一个主题
  void applyTheme(int themeIndex);

  // 设置圆角风格
  void setupRoundedStyle();

  // 获取当前主题的索引
  int &getCurrentThemeIndex() { return current_theme_index_; }

private:
  int current_theme_index_;
};

#endif // THEME_MANAGER_HPP
