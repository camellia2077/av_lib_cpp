// view/imgui/impl/imgui_settings_store.hpp
#ifndef IMGUI_SETTINGS_STORE_HPP
#define IMGUI_SETTINGS_STORE_HPP

#include "imgui.h"
#include "imgui_internal.h"
#include "view/framework/settings_store.hpp"
#include "view/imgui/impl/theme_manager.hpp"

class ImGuiSettingsStore : public SettingsStore {
public:
  explicit ImGuiSettingsStore(ThemeManager &theme_manager);
  void registerSettingsHandler() override;

private:
  static void *readOpen(ImGuiContext *ctx, ImGuiSettingsHandler *handler,
                        const char *name);
  static void readLine(ImGuiContext *ctx, ImGuiSettingsHandler *handler,
                       void *entry, const char *line);
  static void writeAll(ImGuiContext *ctx, ImGuiSettingsHandler *handler,
                       ImGuiTextBuffer *buf);

  ThemeManager &theme_manager_;
  static ImGuiSettingsStore *instance_for_callback_;
};

#endif
