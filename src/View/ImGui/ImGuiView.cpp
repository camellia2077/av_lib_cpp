// View/ImGui/ImGuiView.cpp
#include "ImGuiView.hpp"
#include "UIConfig.hpp"
#include "imgui.h"
#include "imgui_internal.h"
#include "imgui_impl_glfw.h"
#include "imgui_impl_opengl3.h"
#include <GLFW/glfw3.h>
#include <iostream>

// --- 所有主题相关的代码都已移至 ThemeManager ---

static void glfw_error_callback(int error, const char* description) {
    std::cerr << "Glfw Error " << error << ": " << description << std::endl;
}

ImGuiView::ImGuiView(Application& app)
    : app_(app), window_(nullptr) 
{
    theme_manager_ = std::make_unique<ThemeManager>();
    // 将ThemeManager的引用注入到UIPanel中
    ui_panel_ = std::make_unique<UIPanel>(app_, *theme_manager_);
}

bool ImGuiView::init() {
    glfwSetErrorCallback(glfw_error_callback);
    if (!glfwInit()) return false;

    const char* glsl_version = "#version 130";
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);

    window_ = glfwCreateWindow(600, 500, UIConfig::MainWindowTitle, nullptr, nullptr);
    if (window_ == nullptr) return false;
    glfwMakeContextCurrent(window_);
    glfwSwapInterval(1);

    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO();
    io.IniFilename = "imgui.ini";
    
    // 通过ThemeManager注册设置
    theme_manager_->registerSettingsHandler();

    io.Fonts->AddFontFromFileTTF(UIConfig::FontPath, UIConfig::DefaultFontSize, nullptr, io.Fonts->GetGlyphRangesChineseFull());

    // 初始化时应用主题和风格
    theme_manager_->applyTheme(theme_manager_->getCurrentThemeIndex());
    theme_manager_->setupRoundedStyle();

    ImGui_ImplGlfw_InitForOpenGL(window_, true);
    ImGui_ImplOpenGL3_Init(glsl_version);
    
    return true;
}

// ... run() 和 cleanup() 函数保持不变 ...
void ImGuiView::run() {
    app_.load_database();

    while (!glfwWindowShouldClose(window_)) {
        glfwPollEvents();
        render_frame();
        glfwSwapBuffers(window_);
    }
}

void ImGuiView::cleanup() {
    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();
    glfwDestroyWindow(window_);
    glfwTerminate();
}

void ImGuiView::render_frame() {
    ImGui_ImplOpenGL3_NewFrame();
    ImGui_ImplGlfw_NewFrame();
    ImGui::NewFrame();
    
    ImGui::SetNextWindowPos(ImVec2(0, 0));
    ImGui::SetNextWindowSize(ImGui::GetIO().DisplaySize);
    ImGui::Begin("主面板", nullptr, ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoResize);

    ui_panel_->render();

    ImGui::End();

    ImGui::Render();
    int display_w, display_h;
    glfwGetFramebufferSize(window_, &display_w, &display_h);
    glViewport(0, 0, display_w, display_h);
    glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT);
    ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
}