#pragma once

#include "IGuiView.h"

struct GLFWwindow;

class ImGuiView : public IGuiView {
public:
    // ImGui的实现需要一个指向Application的引用来交互
    explicit ImGuiView(Application& app);
    ~ImGuiView() override = default;

    bool init() override;
    void run() override;
    void cleanup() override;

private:
    void render_frame(); // 负责渲染一帧的GUI

    Application& app_; // 对应用逻辑层的引用
    GLFWwindow* window_;
};