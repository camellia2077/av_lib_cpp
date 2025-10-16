// View/ImGui/UIPanel.hpp
#ifndef U_I_PANEL_HPP
#define U_I_PANEL_HPP

#include "App/Application.hpp"
#include "ThemeManager.hpp" // 包含ThemeManager
#include <string>

class UIPanel {
public:
    // 构造函数现在接收一个ThemeManager的引用
    explicit UIPanel(Application& app, ThemeManager& theme_manager);

    void render();

private:
    void update_status_message();

    Application& app_;
    ThemeManager& theme_manager_; // 保存对ThemeManager的引用

    char add_buffer_[128];
    char query_buffer_[128];
    char new_db_name_buffer_[128];
    std::string status_message_;
};

#endif // U_I_PANEL_HPP