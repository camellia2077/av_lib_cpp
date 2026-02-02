// view/imgui/impl/theme_manager.cpp
#include "view/imgui/impl/theme_manager.hpp"
#include "view/imgui/impl/ui_config.hpp"

enum Theme { THEME_DARK, THEME_LIGHT, THEME_CLASSIC };

ThemeManager::ThemeManager() : current_theme_index_(THEME_LIGHT) {}

void ThemeManager::applyTheme(int themeIndex) {
  current_theme_index_ = themeIndex;
  switch (themeIndex) {
  case THEME_DARK:
    ImGui::StyleColorsDark();
    break;
  case THEME_LIGHT:
    ImGui::StyleColorsLight();
    break;
  case THEME_CLASSIC:
    ImGui::StyleColorsClassic();
    break;
  }
}

void ThemeManager::setupRoundedStyle() {
  ImGuiStyle &style = ImGui::GetStyle();
  // --- [FIX] Use '::' for namespaces, not '.' ---
  style.WindowRounding = UIConfig::CornerRounding;
  style.ChildRounding = UIConfig::CornerRounding;
  style.FrameRounding = UIConfig::CornerRounding;
  style.PopupRounding = UIConfig::CornerRounding;
  style.GrabRounding = UIConfig::CornerRounding;
  style.TabRounding = UIConfig::CornerRounding;
}
