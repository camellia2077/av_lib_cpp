// View/ImGui/ImGuiView.hpp
#ifndef IM_GUI_VIEW_HPP
#define IM_GUI_VIEW_HPP

#include "View/IGuiView.hpp"
#include "UIPanel.hpp"
#include "ThemeManager.hpp" // 包含ThemeManager
#include <memory>

struct GLFWwindow;

class ImGuiView : public IGuiView {
public:
    explicit ImGuiView(Application& app);
    ~ImGuiView() override = default;

    bool init() override;
    void run() override;
    void cleanup() override;

private:
    void render_frame();

    Application& app_;
    GLFWwindow* window_;
    
    std::unique_ptr<ThemeManager> theme_manager_; // 拥有ThemeManager
    std::unique_ptr<UIPanel> ui_panel_;
};

#endif // IM_GUI_VIEW_HPP