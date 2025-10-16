// View/ImGui/ThemeManager.hpp
#ifndef THEME_MANAGER_HPP
#define THEME_MANAGER_HPP

#include "imgui.h"
#include "imgui_internal.h" // --- [FIX] Include the internal header for handler types ---

// 将主题相关的实现细节封装起来
class ThemeManager {
public:
    ThemeManager();

    // 应用一个主题
    void applyTheme(int themeIndex);
    
    // 设置圆角风格
    void setupRoundedStyle();

    // 获取当前主题的索引
    int& getCurrentThemeIndex() { return current_theme_index_; }

    // 向ImGui注册用于保存主题状态的处理器
    void registerSettingsHandler();

private:
    // ImGui设置处理器的回调函数 (设为静态，因为C风格回调无法捕获this)
    static void* readOpen(ImGuiContext* ctx, ImGuiSettingsHandler* handler, const char* name);
    static void readLine(ImGuiContext* ctx, ImGuiSettingsHandler* handler, void* entry, const char* line);
    static void writeAll(ImGuiContext* ctx, ImGuiSettingsHandler* handler, ImGuiTextBuffer* buf);
    
    int current_theme_index_;

    // 使用一个静态成员来让C风格回调可以访问到实例
    static ThemeManager* instance_for_callback_; 
};

#endif // THEME_MANAGER_HPP