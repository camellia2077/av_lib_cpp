#include "common/pch.h"
#include "ImGuiView.h"
#include "UIConfig.h"
#include "imgui.h"
#include "imgui_internal.h"
#include "imgui_impl_glfw.h"
#include "imgui_impl_opengl3.h"
#include <GLFW/glfw3.h>
#include <iostream>
#include <sstream> // for stringstream

// --- 主题定义 (保持不变) ---
enum Theme { THEME_DARK, THEME_LIGHT, THEME_CLASSIC };
static int g_CurrentThemeIndex = THEME_CLASSIC;

static void ApplyTheme(int themeIndex) {
    g_CurrentThemeIndex = themeIndex;
    switch (themeIndex) {
        case THEME_DARK:    ImGui::StyleColorsDark();     break;
        case THEME_LIGHT:   ImGui::StyleColorsLight();    break;
        case THEME_CLASSIC: ImGui::StyleColorsClassic();  break;
    }
}

// --- 其他辅助函数 (保持不变) ---
static void glfw_error_callback(int error, const char* description) {
    std::cerr << "Glfw Error " << error << ": " << description << std::endl;
}

static void SetupRoundedStyle() {
    ImGuiStyle& style = ImGui::GetStyle();
    style.WindowRounding = UIConfig::CornerRounding;
    style.ChildRounding = UIConfig::CornerRounding;
    style.FrameRounding = UIConfig::CornerRounding;
    style.PopupRounding = UIConfig::CornerRounding;
    style.GrabRounding = UIConfig::CornerRounding;
    style.TabRounding = UIConfig::CornerRounding;
}

static void* ThemeSettings_ReadOpen(ImGuiContext* ctx, ImGuiSettingsHandler* handler, const char* name) { return &g_CurrentThemeIndex; }
static void ThemeSettings_ReadLine(ImGuiContext* ctx, ImGuiSettingsHandler* handler, void* entry, const char* line) { int theme_index; if (sscanf(line, "Theme=%d", &theme_index) == 1) ApplyTheme(theme_index); }
static void ThemeSettings_WriteAll(ImGuiContext* ctx, ImGuiSettingsHandler* handler, ImGuiTextBuffer* buf) { buf->appendf("[%s][State]\nTheme=%d\n\n", handler->TypeName, g_CurrentThemeIndex); }

// --- ImGuiView 实现 ---

ImGuiView::ImGuiView(Application& app) 
    : app_(app), window_(nullptr) 
{
    // 初始化缓冲区
    add_buffer_[0] = '\0';
    query_buffer_[0] = '\0';
    new_db_name_buffer_[0] = '\0';
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
    update_status_message(); // 初始化后更新一次状态

    while (!glfwWindowShouldClose(window_)) {
        glfwPollEvents();
        render_frame();
        glfwSwapBuffers(window_);
    }
}

void ImGuiView::update_status_message() {
    // 核心逻辑：将 AppStatus 翻译成 UI 文本
    AppStatus status = app_.get_status();
    const auto& result = app_.get_operation_result();

    switch (status) {
        case AppStatus::Idle:             status_message_ = UIConfig::Messages::Idle; break;
        case AppStatus::Welcome:          status_message_ = UIConfig::Messages::Welcome; break;
        case AppStatus::DBLoadSuccess:    status_message_ = UIConfig::Messages::DBLoadSuccess; break;
        case AppStatus::DBSwitched:       status_message_ = UIConfig::Messages::dbSwitched(app_.get_current_db_name()); break;
        case AppStatus::DBCreated:        status_message_ = UIConfig::Messages::dbCreated(app_.get_current_db_name()); break;
        case AppStatus::AddCompleted:     status_message_ = UIConfig::Messages::addCompleted(result); break;
        case AppStatus::QueryCompleted:   status_message_ = UIConfig::Messages::queryCompleted(result); break;
        case AppStatus::ErrorDBNotExist:  status_message_ = UIConfig::Messages::ErrorDBNotExist; break;
        case AppStatus::ErrorDBCreateFailed: status_message_ = UIConfig::Messages::ErrorDBCreateFailed; break;
        case AppStatus::ErrorDBNameExists: status_message_ = UIConfig::Messages::ErrorDBNameExists; break;
        case AppStatus::ErrorDBNameEmpty: status_message_ = UIConfig::Messages::ErrorDBNameEmpty; break;
        case AppStatus::ErrorAddIDEmpty:  status_message_ = UIConfig::Messages::ErrorAddIDEmpty; break;
        case AppStatus::ErrorQueryIDEmpty: status_message_ = UIConfig::Messages::ErrorQueryIDEmpty; break;
        default: status_message_ = "未知状态。"; break;
    }
}

void ImGuiView::render_frame() {
    ImGui_ImplOpenGL3_NewFrame();
    ImGui_ImplGlfw_NewFrame();
    ImGui::NewFrame();
    
    ImGui::SetNextWindowPos(ImVec2(0, 0));
    ImGui::SetNextWindowSize(ImGui::GetIO().DisplaySize);
    ImGui::Begin("主面板", nullptr, ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoMove | ImGuiWindowFlags_NoResize);

    // --- 数据库和主题选择 (与之前类似) ---
    ImGui::Text(UIConfig::CurrentDbLabel);
    const std::string& current_db = app_.get_current_db_name();
    if (ImGui::BeginCombo("##db_combo", current_db.c_str())) {
        for (const auto& db_name : app_.get_database_names()) {
            if (ImGui::Selectable(db_name.c_str(), current_db == db_name)) {
                app_.set_current_database(db_name);
                update_status_message(); // 切换后更新消息
            }
        }
        ImGui::EndCombo();
    }
    
    const char* themes[] = { "默认暗色", "明亮", "经典复古" };
    if (ImGui::Combo("主题选择", &g_CurrentThemeIndex, themes, IM_ARRAYSIZE(themes))) {
        ApplyTheme(g_CurrentThemeIndex);
        SetupRoundedStyle();
        ImGui::MarkIniSettingsDirty();
    }
    ImGui::Separator();

    // --- 内容存入区域 ---
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
    ImGui::Separator();
    ImGui::Text("字体: %s", UIConfig::FontPath);

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