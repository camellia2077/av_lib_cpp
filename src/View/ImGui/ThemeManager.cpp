// View/ImGui/ThemeManager.cpp
#include "ThemeManager.hpp"
#include "UIConfig.hpp"
// 初始化静态成员
ThemeManager* ThemeManager::instance_for_callback_ = nullptr;

enum Theme { THEME_DARK, THEME_LIGHT, THEME_CLASSIC };

ThemeManager::ThemeManager() : current_theme_index_(THEME_CLASSIC) {
    // 在构造时将自己注册为回调实例
    instance_for_callback_ = this;
}

void ThemeManager::applyTheme(int themeIndex) {
    current_theme_index_ = themeIndex;
    switch (themeIndex) {
        case THEME_DARK:    ImGui::StyleColorsDark();     break;
        case THEME_LIGHT:   ImGui::StyleColorsLight();    break;
        case THEME_CLASSIC: ImGui::StyleColorsClassic();  break;
    }
}

void ThemeManager::setupRoundedStyle() {
    ImGuiStyle& style = ImGui::GetStyle();
    // --- [FIX] Use '::' for namespaces, not '.' ---
    style.WindowRounding = UIConfig::CornerRounding;
    style.ChildRounding = UIConfig::CornerRounding;
    style.FrameRounding = UIConfig::CornerRounding;
    style.PopupRounding = UIConfig::CornerRounding;
    style.GrabRounding = UIConfig::CornerRounding;
    style.TabRounding = UIConfig::CornerRounding;
}

void ThemeManager::registerSettingsHandler() {
    ImGuiSettingsHandler ini_handler;
    ini_handler.TypeName = "AppSettings";
    ini_handler.TypeHash = ImHashStr("AppSettings");
    ini_handler.ReadOpenFn = ThemeManager::readOpen;
    ini_handler.ReadLineFn = ThemeManager::readLine;
    ini_handler.WriteAllFn = ThemeManager::writeAll;
    ImGui::AddSettingsHandler(&ini_handler);
}

// --- 回调实现 ---
void* ThemeManager::readOpen(ImGuiContext*, ImGuiSettingsHandler*, const char*) {
    // 返回一个非空指针即可，我们通过静态实例来操作
    return instance_for_callback_;
}

void ThemeManager::readLine(ImGuiContext*, ImGuiSettingsHandler*, void*, const char* line) {
    int theme_index;
    if (sscanf(line, "Theme=%d", &theme_index) == 1) {
        if(instance_for_callback_) {
            instance_for_callback_->applyTheme(theme_index);
        }
    }
}

void ThemeManager::writeAll(ImGuiContext*, ImGuiSettingsHandler* handler, ImGuiTextBuffer* buf) {
    if (instance_for_callback_) {
        buf->appendf("[%s][State]\nTheme=%d\n\n", handler->TypeName, instance_for_callback_->current_theme_index_);
    }
}