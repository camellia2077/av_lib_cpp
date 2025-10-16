// View/ImGui/UIPanel.cpp
#include "UIPanel.hpp"
#include "UIConfig.hpp"
#include "common/MessageFormatter.hpp"
#include "common/version.hpp"
#include "imgui.h"
#include "imgui_internal.h"

// --- 不再需要 extern 和全局函数声明 ---

UIPanel::UIPanel(Application& app, ThemeManager& theme_manager) 
    : app_(app), theme_manager_(theme_manager) { // 保存引用
    add_buffer_[0] = '\0';
    query_buffer_[0] = '\0';
    new_db_name_buffer_[0] = '\0';
    update_status_message();
}

void UIPanel::update_status_message() {
    status_message_ = MessageFormatter::format_message(app_);
}

void UIPanel::render() {
    // ... 其他UI渲染代码不变 ...
    
    const std::string& current_db = app_.get_current_db_name();
    if (ImGui::BeginCombo("##db_combo", current_db.c_str())) { /* ... */ }

    const char* themes[] = { "默认暗色", "明亮", "经典复古" };
    // 使用注入的 theme_manager_ 来访问和修改主题
    if (ImGui::Combo("主题选择", &theme_manager_.getCurrentThemeIndex(), themes, IM_ARRAYSIZE(themes))) {
        theme_manager_.applyTheme(theme_manager_.getCurrentThemeIndex());
        theme_manager_.setupRoundedStyle();
        ImGui::MarkIniSettingsDirty();
    }
    ImGui::Separator();

    // ... 剩余的渲染代码完全不变 ...
    ImGui::Text(UIConfig::AddSectionHeader);
    ImGui::PushItemWidth(ImGui::GetContentRegionAvail().x * 0.7f);
    if (ImGui::InputText("##add_id", add_buffer_, sizeof(add_buffer_), ImGuiInputTextFlags_EnterReturnsTrue)) {
        app_.perform_add(add_buffer_);
        update_status_message();
        if(app_.get_status() == AppStatus::AddCompleted && app_.get_operation_result().success_count > 0) add_buffer_[0] = '\0';
    }
    ImGui::PopItemWidth();
    ImGui::SameLine();
    if (ImGui::Button(UIConfig::AddToCurrentDbButton)) {
        app_.perform_add(add_buffer_);
        update_status_message();
        if(app_.get_status() == AppStatus::AddCompleted && app_.get_operation_result().success_count > 0) add_buffer_[0] = '\0';
    }

    ImGui::Spacing();
    ImGui::PushItemWidth(ImGui::GetContentRegionAvail().x * 0.7f);
    ImGui::InputTextWithHint("##new_db_name", UIConfig::NewDbInputHint, new_db_name_buffer_, sizeof(new_db_name_buffer_));
    ImGui::PopItemWidth();
    ImGui::SameLine();
    if (ImGui::Button(UIConfig::CreateNewDbButton)) {
        app_.perform_create_database(new_db_name_buffer_);
        update_status_message();
        if(app_.get_status() == AppStatus::DBCreated) new_db_name_buffer_[0] = '\0';
    }

    ImGui::Separator();

    // --- 内容查询区域 ---
    ImGui::Text(UIConfig::QuerySectionHeader, current_db.c_str());
    ImGui::PushItemWidth(ImGui::GetContentRegionAvail().x * 0.7f);
    if (ImGui::InputText("##query_id", query_buffer_, sizeof(query_buffer_), ImGuiInputTextFlags_EnterReturnsTrue)) {
        app_.perform_query(query_buffer_);
        update_status_message();
    }
    ImGui::PopItemWidth();
    ImGui::SameLine();
    if (ImGui::Button(UIConfig::QueryButton)) {
        app_.perform_query(query_buffer_);
        update_status_message();
    }

    ImGui::Separator();

    // --- 状态栏 ---
    ImGui::Text(UIConfig::StatusLabel, status_message_.c_str());
    ImGui::Text(UIConfig::TotalRecordsLabel, app_.get_total_records());

    auto version_text = std::string("Version: ") + std::string(AppVersion::VersionString);
    auto text_width = ImGui::CalcTextSize(version_text.c_str()).x;
    ImGui::SameLine(ImGui::GetWindowWidth() - text_width - ImGui::GetStyle().WindowPadding.x);
    ImGui::Text("%s", version_text.c_str());

    ImGui::Separator();
    ImGui::Text("字体: %s", UIConfig::FontPath);
}