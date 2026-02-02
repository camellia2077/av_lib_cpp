// view/imgui/impl/theme_manager.cpp
#include "view/imgui/impl/theme_manager.hpp"

#include "view/imgui/impl/ui_config.hpp"

enum Theme { kThemeDark, kThemeLight, kThemeClassic };

ThemeManager::ThemeManager() {}

void ThemeManager::ApplyTheme(int theme_index) {
  current_theme_index_ = theme_index;
  switch (theme_index) {
    case kThemeDark:
      ImGui::StyleColorsDark();
      break;
    case kThemeLight:
      ImGui::StyleColorsLight();
      break;
    case kThemeClassic:
      ImGui::StyleColorsClassic();
      break;
  }
}

void ThemeManager::SetupRoundedStyle() {
  ImGuiStyle& style = ImGui::GetStyle();
  style.WindowRounding = UIConfig::kCornerRounding;
  style.ChildRounding = UIConfig::kCornerRounding;
  style.FrameRounding = UIConfig::kCornerRounding;
  style.PopupRounding = UIConfig::kCornerRounding;
  style.GrabRounding = UIConfig::kCornerRounding;
  style.TabRounding = UIConfig::kCornerRounding;
}
