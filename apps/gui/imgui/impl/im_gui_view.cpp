// apps/gui/imgui/impl/im_gui_view.cpp
#include "apps/gui/imgui/impl/im_gui_view.hpp"

#include <GLFW/glfw3.h>

#include <iostream>

#include "imgui.h"
#include "imgui_impl_glfw.h"
#include "imgui_impl_opengl3.h"
#include "imgui_internal.h"
#include "apps/gui/imgui/impl/ui_config.hpp"

// --- 所有主题相关的代码都已移至 ThemeManager ---

static void GlfwErrorCallback(int error, const char* description) {
  std::cerr << "Glfw Error " << error << ": " << description << std::endl;
}

ImGuiView::ImGuiView(Application& app) : app_(app) {
  theme_manager_ = std::make_unique<ThemeManager>();
  settings_store_ = std::make_unique<ImGuiSettingsStore>(*theme_manager_);
  // 将ThemeManager的引用注入到UIPanel中
  ui_panel_ = std::make_unique<UIPanel>(app_, *theme_manager_);
}

auto ImGuiView::Init() -> bool {
  glfwSetErrorCallback(GlfwErrorCallback);
  if (glfwInit() == 0) {
    return false;
  }

  const char* glsl_version = "#version 130";
  glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
  glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);

  window_ =
      glfwCreateWindow(600, 500, UIConfig::kMainWindowTitle, nullptr, nullptr);
  if (window_ == nullptr) {
    return false;
  }
  glfwMakeContextCurrent(window_);
  glfwSwapInterval(1);

  IMGUI_CHECKVERSION();
  ImGui::CreateContext();
  ImGuiIO& io = ImGui::GetIO();
  io.IniFilename = "imgui.ini";

  // 通过SettingsStore注册设置
  settings_store_->RegisterSettingsHandler();

  io.Fonts->AddFontFromFileTTF(UIConfig::kFontPath, UIConfig::kDefaultFontSize,
                               nullptr, io.Fonts->GetGlyphRangesChineseFull());

  // 初始化时应用主题和风格
  theme_manager_->ApplyTheme(theme_manager_->GetCurrentThemeIndex());
  theme_manager_->SetupRoundedStyle();

  ImGui_ImplGlfw_InitForOpenGL(window_, true);
  ImGui_ImplOpenGL3_Init(glsl_version);

  return true;
}

// ... run() 和 cleanup() 函数保持不变 ...
void ImGuiView::Run() {
  app_.LoadDatabase();

  while (glfwWindowShouldClose(window_) == 0) {
    glfwPollEvents();
    RenderFrame();
    glfwSwapBuffers(window_);
  }
}

void ImGuiView::Cleanup() {
  ImGui_ImplOpenGL3_Shutdown();
  ImGui_ImplGlfw_Shutdown();
  ImGui::DestroyContext();
  glfwDestroyWindow(window_);
  glfwTerminate();
}

void ImGuiView::RenderFrame() {
  ImGui_ImplOpenGL3_NewFrame();
  ImGui_ImplGlfw_NewFrame();
  ImGui::NewFrame();

  ImGui::SetNextWindowPos(ImVec2(0, 0));
  ImGui::SetNextWindowSize(ImGui::GetIO().DisplaySize);
  ImGui::Begin("主面板", nullptr,
               ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoMove |
                   ImGuiWindowFlags_NoResize);

  ui_panel_->Render();

  ImGui::End();

  ImGui::Render();
  int display_w;
  int display_h;
  glfwGetFramebufferSize(window_, &display_w, &display_h);
  glViewport(0, 0, display_w, display_h);
  glClearColor(0.1F, 0.1F, 0.1F, 1.0F);
  glClear(GL_COLOR_BUFFER_BIT);
  ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
}

