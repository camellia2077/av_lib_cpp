#include "common/pch.h"
#include "ImGuiView.h"
#include "UIConfig.h"
#include "imgui.h"
#include "imgui_impl_glfw.h"
#include "imgui_impl_opengl3.h"
#include <GLFW/glfw3.h>
#include <iostream>

static void glfw_error_callback(int error, const char* description) {
    std::cerr << "Glfw Error " << error << ": " << description << std::endl;
}

// --- 设置圆角样式的函数 ---
static void SetupRoundedStyle() {
    ImGuiStyle& style = ImGui::GetStyle();

    // 直接使用配置文件中的值
    style.WindowRounding    = UIConfig::CornerRounding;
    style.ChildRounding     = UIConfig::CornerRounding;
    style.FrameRounding     = UIConfig::CornerRounding;
    style.PopupRounding     = UIConfig::CornerRounding;
    style.GrabRounding      = UIConfig::CornerRounding;
    style.TabRounding       = UIConfig::CornerRounding;
}


ImGuiView::ImGuiView(Application& app) : app_(app), window_(nullptr) {}

bool ImGuiView::init() {
    glfwSetErrorCallback(glfw_error_callback);
    if (!glfwInit()) return false;

    const char* glsl_version = "#version 130";
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);

    window_ = glfwCreateWindow(600, 450, UIConfig::MainWindowTitle, nullptr, nullptr);
    if (window_ == nullptr) return false;
    glfwMakeContextCurrent(window_);
    glfwSwapInterval(1);

    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO();
    
    io.Fonts->AddFontFromFileTTF(UIConfig::FontPath, UIConfig::DefaultFontSize, nullptr, io.Fonts->GetGlyphRangesChineseFull());

    ImGui::StyleColorsDark();
    SetupRoundedStyle(); //

    ImGui_ImplGlfw_InitForOpenGL(window_, true);
    ImGui_ImplOpenGL3_Init(glsl_version);
    
    return true;
}

// ... (run, render_frame, 和 cleanup 函数保持不变)
void ImGuiView::run() {
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
    
    ImGui::SetNextWindowPos(ImVec2(0, 0));
    ImGui::SetNextWindowSize(ImGui::GetIO().DisplaySize);
    ImGui::Begin("主面板", nullptr, ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoResize);

    // (数据库选择、编号存入、查询等部分代码保持不变...)
    ImGui::Text(UIConfig::CurrentDbLabel);
    std::vector<std::string> db_names = app_.get_database_names();
    const std::string& current_db = app_.get_current_db_name();
    if (ImGui::BeginCombo("##db_combo", current_db.c_str())) {
        for (const auto& db_name : db_names) {
            const bool is_selected = (current_db == db_name);
            if (ImGui::Selectable(db_name.c_str(), is_selected)) {
                app_.set_current_database(db_name);
            }
            if (is_selected) {
                ImGui::SetItemDefaultFocus();
            }
        }
        ImGui::EndCombo();
    }
    
    ImGui::Separator();

    // --- 编号存入区域 ---
    ImGui::Text(UIConfig::AddSectionHeader);
    
    char add_buf[128];
    strncpy(add_buf, app_.get_add_buffer(), 128);
    ImGui::PushItemWidth(ImGui::GetContentRegionAvail().x * 0.7f);
    // 按回车键现在也只执行添加操作
    if (ImGui::InputText("##add_id", add_buf, IM_ARRAYSIZE(add_buf), ImGuiInputTextFlags_EnterReturnsTrue)) {
        app_.set_add_buffer(add_buf);
        app_.perform_add();
    }
    app_.set_add_buffer(add_buf);
    
    ImGui::PopItemWidth();
    ImGui::SameLine();
    // 这个按钮现在是唯一的添加数据的方式
    if (ImGui::Button(UIConfig::AddToCurrentDbButton)) {
        app_.perform_add();
    }
    
    ImGui::Spacing();
    
    // --- 数据库创建区域 ---
    char new_db_buf[128];
    strncpy(new_db_buf, app_.get_new_db_name_buffer(), 128);
    ImGui::PushItemWidth(ImGui::GetContentRegionAvail().x * 0.7f);
    ImGui::InputTextWithHint("##new_db_name", UIConfig::NewDbInputHint, new_db_buf, IM_ARRAYSIZE(new_db_buf));
    app_.set_new_db_name_buffer(new_db_buf);
    
    ImGui::PopItemWidth();
    ImGui::SameLine();
    // 将按钮绑定到新的 perform_create_database 函数
    if (ImGui::Button(UIConfig::CreateNewDbButton)) {
        app_.perform_create_database();
    }
    
    ImGui::Separator();
    
    ImGui::Text(UIConfig::QuerySectionHeader, current_db.c_str());
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
    if (ImGui::Button(UIConfig::QueryButton)) {
        app_.perform_query();
    }
    
    ImGui::Separator();
    
    // --- 状态信息区域 ---
    ImGui::Text(UIConfig::StatusLabel, app_.get_status_message().c_str());
    ImGui::Text(UIConfig::TotalRecordsLabel, app_.get_total_records());

    // --- 新增：显示当前加载的字体 ---
    ImGui::Separator(); // 加一个分隔线以示区分
    ImGui::Text("Loaded Font: %s", UIConfig::FontPath);


    ImGui::End();

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