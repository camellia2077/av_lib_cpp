// apps/gui/imgui/impl/imgui_settings_store.cpp
#include "apps/gui/imgui/impl/imgui_settings_store.hpp"

#include <cstdio>

#include "imgui.h"
#include "imgui_internal.h"

ImGuiSettingsStore* ImGuiSettingsStore::instance_for_callback_ = nullptr;

ImGuiSettingsStore::ImGuiSettingsStore(ThemeManager& theme_manager)
    : theme_manager_(theme_manager) {
  instance_for_callback_ = this;
}

void ImGuiSettingsStore::RegisterSettingsHandler() {
  ImGuiSettingsHandler ini_handler;
  ini_handler.TypeName = "AppSettings";
  ini_handler.TypeHash = ImHashStr("AppSettings");
  ini_handler.ReadOpenFn = ImGuiSettingsStore::ReadOpen;
  ini_handler.ReadLineFn = ImGuiSettingsStore::ReadLine;
  ini_handler.WriteAllFn = ImGuiSettingsStore::WriteAll;
  ImGui::AddSettingsHandler(&ini_handler);
}

auto ImGuiSettingsStore::ReadOpen(ImGuiContext* /*unused*/,
                                  ImGuiSettingsHandler* /*unused*/,
                                  const char* /*unused*/) -> void* {
  return instance_for_callback_;
}

void ImGuiSettingsStore::ReadLine(ImGuiContext* /*unused*/,
                                  ImGuiSettingsHandler* /*unused*/,
                                  void* /*unused*/, const char* line) {
  int theme_index;
  if (std::sscanf(line, "Theme=%d", &theme_index) == 1) {
    if (instance_for_callback_ != nullptr) {
      instance_for_callback_->theme_manager_.ApplyTheme(theme_index);
    }
  }
}

void ImGuiSettingsStore::WriteAll(ImGuiContext* /*unused*/,
                                  ImGuiSettingsHandler* handler,
                                  ImGuiTextBuffer* buf) {
  if (instance_for_callback_ != nullptr) {
    const int kThemeIndex =
        instance_for_callback_->theme_manager_.GetCurrentThemeIndex();
    buf->appendf("[%s][State]\nTheme=%d\n\n", handler->TypeName, kThemeIndex);
  }
}

