// View/ImGui/ImGuiView.hpp
#ifndef IMGUIVIEW_HPP
#define IMGUIVIEW_HPP

#include "View/IGuiView.hpp"
#include <string>

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
    void update_status_message(); // 新增：一个根据app状态更新消息的辅助函数

    Application& app_;
    GLFWwindow* window_;

    // UI层自己管理输入框的缓冲区和状态消息
    char add_buffer_[128];
    char query_buffer_[128];
    char new_db_name_buffer_[128];
    std::string status_message_;
};
#endif