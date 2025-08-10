#include "common/pch.h"
#include "ImGuiView.h"
#include "imgui.h"
#include "imgui_impl_glfw.h"
#include "imgui_impl_opengl3.h"
#include <GLFW/glfw3.h>
#include <iostream>

// (这里可以放入之前main.cpp中的glfw_error_callback和setup_style函数)
static void glfw_error_callback(int error, const char* description) {
    std::cerr << "Glfw Error " << error << ": " << description << std::endl;
}

ImGuiView::ImGuiView(Application& app) : app_(app), window_(nullptr) {}

bool ImGuiView::init() {
    glfwSetErrorCallback(glfw_error_callback);
    if (!glfwInit()) return false;

    const char* glsl_version = "#version 130";
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);

    window_ = glfwCreateWindow(600, 400, "极速编号查询系统 (解耦版)", nullptr, nullptr);
    if (window_ == nullptr) return false;
    glfwMakeContextCurrent(window_);
    glfwSwapInterval(1);

    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO();
    io.Fonts->AddFontFromFileTTF("c:/windows/fonts/msyh.ttc", 18.0f, nullptr, io.Fonts->GetGlyphRangesChineseFull());

    ImGui::StyleColorsDark();

    ImGui_ImplGlfw_InitForOpenGL(window_, true);
    ImGui_ImplOpenGL3_Init(glsl_version);
    
    return true;
}

void ImGuiView::run() {
    // 启动时先加载数据库
    app_.load_database();

    while (!glfwWindowShouldClose(window_)) {
        glfwPollEvents();
        render_frame();
        glfwSwapBuffers(window_);
    }
}

void ImGuiView::render_frame() {
    ImGui_ImplOpenGL3_NewFrame();
    ImGui_ImplGlfw_NewFrame();
    ImGui::NewFrame();
    
    // --- GUI 布局 ---
    ImGui::SetNextWindowPos(ImVec2(0, 0));
    ImGui::SetNextWindowSize(ImGui::GetIO().DisplaySize);
    ImGui::Begin("主面板", nullptr, ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoResize);

    ImGui::Text("编号存入");
    // 从App层获取缓冲区数据来显示，并将用户的输入更新回App层
    char add_buf[128];
    strncpy(add_buf, app_.get_add_buffer(), 128);
    ImGui::PushItemWidth(ImGui::GetContentRegionAvail().x * 0.7f);
    if (ImGui::InputText("##add_id", add_buf, IM_ARRAYSIZE(add_buf), ImGuiInputTextFlags_EnterReturnsTrue)) {
        app_.set_add_buffer(add_buf);
        app_.perform_add(); // 通知App层执行动作
    }
    app_.set_add_buffer(add_buf); // 持续更新缓冲区
    
    ImGui::PopItemWidth();
    ImGui::SameLine();
    if (ImGui::Button("添加")) {
        app_.perform_add(); // 通知App层执行动作
    }
    
    ImGui::Separator();
    
    ImGui::Text("编号查询");
    char query_buf[128];
    strncpy(query_buf, app_.get_query_buffer(), 128);
    ImGui::PushItemWidth(ImGui::GetContentRegionAvail().x * 0.7f);
    if (ImGui::InputText("##query_id", query_buf, IM_ARRAYSIZE(query_buf), ImGuiInputTextFlags_EnterReturnsTrue)) {
        app_.set_query_buffer(query_buf);
        app_.perform_query();
    }
    app_.set_query_buffer(query_buf);
    
    ImGui::PopItemWidth();
    ImGui::SameLine();
    if (ImGui::Button("查询")) {
        app_.perform_query();
    }
    
    ImGui::Separator();
    
    // 从App层获取状态信息来显示
    ImGui::Text("状态: %s", app_.get_status_message().c_str());
    ImGui::Text("当前记录总数: %zu", app_.get_total_records());

    ImGui::End();

    // 渲染
    ImGui::Render();
    int display_w, display_h;
    glfwGetFramebufferSize(window_, &display_w, &display_h);
    glViewport(0, 0, display_w, display_h);
    glClearColor(0.1f, 0.1f, 0.1f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT);
    ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
}

void ImGuiView::cleanup() {
    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();
    glfwDestroyWindow(window_);
    glfwTerminate();
}