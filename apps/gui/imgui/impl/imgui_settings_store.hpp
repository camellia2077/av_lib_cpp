// apps/gui/imgui/impl/imgui_settings_store.hpp
#ifndef IMGUI_SETTINGS_STORE_HPP
#define IMGUI_SETTINGS_STORE_HPP

#include "imgui.h"
#include "imgui_internal.h"
#include "apps/gui/framework/settings_store.hpp"
#include "apps/gui/imgui/impl/theme_manager.hpp"

class ImGuiSettingsStore : public SettingsStore {
 public:
  explicit ImGuiSettingsStore(ThemeManager& theme_manager);
  void RegisterSettingsHandler() override;

 private:
  static auto ReadOpen(ImGuiContext* ctx, ImGuiSettingsHandler* handler,
                       const char* name) -> void*;
  static void ReadLine(ImGuiContext* ctx, ImGuiSettingsHandler* handler,
                       void* entry, const char* line);
  static void WriteAll(ImGuiContext* ctx, ImGuiSettingsHandler* handler,
                       ImGuiTextBuffer* buf);

  ThemeManager& theme_manager_;
  static ImGuiSettingsStore* instance_for_callback_;
};

#endif

