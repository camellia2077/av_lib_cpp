// view/imgui/impl/imgui_settings_store.cpp
#include "view/imgui/impl/imgui_settings_store.hpp"
#include "imgui.h"
#include "imgui_internal.h"
#include <cstdio>

ImGuiSettingsStore *ImGuiSettingsStore::instance_for_callback_ = nullptr;

ImGuiSettingsStore::ImGuiSettingsStore(ThemeManager &theme_manager)
    : theme_manager_(theme_manager) {
  instance_for_callback_ = this;
}

void ImGuiSettingsStore::registerSettingsHandler() {
  ImGuiSettingsHandler ini_handler;
  ini_handler.TypeName = "AppSettings";
  ini_handler.TypeHash = ImHashStr("AppSettings");
  ini_handler.ReadOpenFn = ImGuiSettingsStore::readOpen;
  ini_handler.ReadLineFn = ImGuiSettingsStore::readLine;
  ini_handler.WriteAllFn = ImGuiSettingsStore::writeAll;
  ImGui::AddSettingsHandler(&ini_handler);
}

void *ImGuiSettingsStore::readOpen(ImGuiContext *, ImGuiSettingsHandler *,
                                   const char *) {
  return instance_for_callback_;
}

void ImGuiSettingsStore::readLine(ImGuiContext *, ImGuiSettingsHandler *,
                                  void *, const char *line) {
  int theme_index;
  if (std::sscanf(line, "Theme=%d", &theme_index) == 1) {
    if (instance_for_callback_) {
      instance_for_callback_->theme_manager_.applyTheme(theme_index);
    }
  }
}

void ImGuiSettingsStore::writeAll(ImGuiContext *, ImGuiSettingsHandler *handler,
                                  ImGuiTextBuffer *buf) {
  if (instance_for_callback_) {
    const int theme_index =
        instance_for_callback_->theme_manager_.getCurrentThemeIndex();
    buf->appendf("[%s][State]\nTheme=%d\n\n", handler->TypeName, theme_index);
  }
}
