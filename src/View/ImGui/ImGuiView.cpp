#include "common/pch.h"
#include "ImGuiView.h"
#include "UIConfig.h"
#include "imgui.h"
#include "imgui_internal.h" // 需要包含 internal 头文件以使用设置处理器
#include "imgui_impl_glfw.h"
#include "imgui_impl_opengl3.h"
#include <GLFW/glfw3.h>
#include <iostream>

// --- 主题定义 ---
enum Theme {
    THEME_DARK,
    THEME_LIGHT,
    THEME_CLASSIC
};

// 全局静态变量，用于存储当前主题的选择，默认为暗色主题
static int g_CurrentThemeIndex = THEME_CLASSIC;
// THEME_DARK;

// --- 主题应用函数 ---
static void ApplyTheme(int themeIndex) {
    g_CurrentThemeIndex = themeIndex;
    switch (themeIndex) {
        case THEME_DARK:    ImGui::StyleColorsDark();     break;
        case THEME_LIGHT:   ImGui::StyleColorsLight();    break;
        case THEME_CLASSIC: ImGui::StyleColorsClassic();  break;
        default:            ImGui::StyleColorsDark();     break;
    }
}

// --- 错误回调和圆角样式 ---
static void glfw_error_callback(int error, const char* description) {
    std::cerr << "Glfw Error " << error << ": " << description << std::endl;
}

static void SetupRoundedStyle() {
    ImGuiStyle& style = ImGui::GetStyle();
    style.WindowRounding    = UIConfig::CornerRounding;
    style.ChildRounding     = UIConfig::CornerRounding;
    style.FrameRounding     = UIConfig::CornerRounding;
    style.PopupRounding     = UIConfig::CornerRounding;
    style.GrabRounding      = UIConfig::CornerRounding;
    style.TabRounding       = UIConfig::CornerRounding;
}


// --- 自定义设置处理器 (保持不变) ---
static void* ThemeSettings_ReadOpen(ImGuiContext* ctx, ImGuiSettingsHandler* handler, const char* name) {
    return &g_CurrentThemeIndex;
}

static void ThemeSettings_ReadLine(ImGuiContext* ctx, ImGuiSettingsHandler* handler, void* entry, const char* line) {
    int theme_index;
    if (sscanf(line, "Theme=%d", &theme_index) == 1) {
        ApplyTheme(theme_index);
    }
}

static void ThemeSettings_WriteAll(ImGuiContext* ctx, ImGuiSettingsHandler* handler, ImGuiTextBuffer* buf) {
    buf->reserve(buf->size() + 50);
    buf->appendf("[%s][State]\n", handler->TypeName);
    buf->appendf("Theme=%d\n", g_CurrentThemeIndex);
    buf->append("\n");
}


ImGuiView::ImGuiView(Application& app) : app_(app), window_(nullptr) {}

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
    
    ImGuiSettingsHandler ini_handler;
    ini_handler.TypeName = "AppSettings";
    ini_handler.TypeHash = ImHashStr("AppSettings");
    ini_handler.ReadOpenFn = ThemeSettings_ReadOpen;
    ini_handler.ReadLineFn = ThemeSettings_ReadLine;
    ini_handler.WriteAllFn = ThemeSettings_WriteAll;
    ImGui::AddSettingsHandler(&ini_handler);

    io.Fonts->AddFontFromFileTTF(UIConfig::FontPath, UIConfig::DefaultFontSize, nullptr, io.Fonts->GetGlyphRangesChineseFull());

    ApplyTheme(g_CurrentThemeIndex);
    SetupRoundedStyle();

    ImGui_ImplGlfw_InitForOpenGL(window_, true);
    ImGui_ImplOpenGL3_Init(glsl_version);
    
    return true;
}

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

    // --- 关键修改：将两个下拉菜单都放到顶部 ---

    // 1. 数据库选择
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
    
    // 2. 主题选择
    const char* themes[] = { "默认暗色 (Dark)", "明亮 (Light)", "经典复古 (Classic)" };
    if (ImGui::Combo("主题选择", &g_CurrentThemeIndex, themes, IM_ARRAYSIZE(themes))) {
        ApplyTheme(g_CurrentThemeIndex);
        SetupRoundedStyle(); // 切换主题后需要重新应用圆角
        ImGui::MarkIniSettingsDirty(); // 标记以便保存
    }

    ImGui::Separator(); // 在顶部设置区下方加一个分隔线

    // (其余的UI部分保持不变...)
    ImGui::Text(UIConfig::AddSectionHeader);
    
    char add_buf[128];
    strncpy(add_buf, app_.get_add_buffer(), 128);
    ImGui::PushItemWidth(ImGui::GetContentRegionAvail().x * 0.7f);
    if (ImGui::InputText("##add_id", add_buf, IM_ARRAYSIZE(add_buf), ImGuiInputTextFlags_EnterReturnsTrue)) {
        app_.set_add_buffer(add_buf);
        app_.perform_add();
    }
    app_.set_add_buffer(add_buf);
    
    ImGui::PopItemWidth();
    ImGui::SameLine();
    if (ImGui::Button(UIConfig::AddToCurrentDbButton)) {
        app_.perform_add();
    }
    
    ImGui::Spacing();
    
    char new_db_buf[128];
    strncpy(new_db_buf, app_.get_new_db_name_buffer(), 128);
    ImGui::PushItemWidth(ImGui::GetContentRegionAvail().x * 0.7f);
    ImGui::InputTextWithHint("##new_db_name", UIConfig::NewDbInputHint, new_db_buf, IM_ARRAYSIZE(new_db_buf));
    app_.set_new_db_name_buffer(new_db_buf);
    
    ImGui::PopItemWidth();
    ImGui::SameLine();
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
    
    ImGui::Text(UIConfig::StatusLabel, app_.get_status_message().c_str());
    ImGui::Text(UIConfig::TotalRecordsLabel, app_.get_total_records());
    ImGui::Separator();
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