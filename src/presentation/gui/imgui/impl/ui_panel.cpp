// view/imgui/impl/ui_panel.cpp
#include "presentation/gui/imgui/impl/ui_panel.hpp"

#include <filesystem>
#include <fstream>
#include <stdexcept>

#include "presentation/cli/input_parser.hpp"
#include "common/version.hpp"
#include "core/io/text_file_reader.hpp"
#include "imgui.h"
#include "imgui_internal.h"
#include "presentation/gui/imgui/im_gui_presenter.hpp"
#include "presentation/gui/imgui/impl/ui_config.hpp"

// --- 不再需要 extern 和全局函数声明 ---

UIPanel::UIPanel(Application& app, ThemeManager& theme_manager)
    : app_(app), theme_manager_(theme_manager) {
  add_buffer_[0] = '\0';
  query_buffer_[0] = '\0';
  new_db_name_buffer_[0] = '\0';
  import_path_buffer_[0] = '\0';
  export_path_buffer_[0] = '\0';
  UpdateStatusMessage();
}

void UIPanel::UpdateStatusMessage() {
  status_message_ = ImGuiPresenter::Format(app_);
}

void UIPanel::Render() {
  // ... 其他UI渲染代码不变 ...

  const std::string& current_db = app_.GetCurrentDbName();
  if (ImGui::BeginCombo("##db_combo", current_db.c_str())) { /* ... */
  }

  const char* themes[] = {"默认暗色", "明亮", "经典复古"};
  if (ImGui::Combo("主题选择", &theme_manager_.GetCurrentThemeIndex(), themes,
                   IM_ARRAYSIZE(themes))) {
    theme_manager_.ApplyTheme(theme_manager_.GetCurrentThemeIndex());
    theme_manager_.SetupRoundedStyle();
    ImGui::MarkIniSettingsDirty();
  }
  ImGui::Separator();

  ImGui::Text(UIConfig::kAddSectionHeader);
  ImGui::PushItemWidth(ImGui::GetContentRegionAvail().x * 0.7F);
  if (ImGui::InputText("##add_id", add_buffer_, sizeof(add_buffer_),
                       ImGuiInputTextFlags_EnterReturnsTrue)) {
    app_.PerformAdd(Adapters::SplitIds(add_buffer_));
    UpdateStatusMessage();
    if (app_.GetLastResult() == ResultCode::kAddCompleted &&
        app_.GetLastAddResult().success_count > 0) {
      add_buffer_[0] = '\0';
    }
  }
  ImGui::PopItemWidth();
  ImGui::SameLine();
  if (ImGui::Button(UIConfig::kAddToCurrentDbButton)) {
    app_.PerformAdd(Adapters::SplitIds(add_buffer_));
    UpdateStatusMessage();
    if (app_.GetLastResult() == ResultCode::kAddCompleted &&
        app_.GetLastAddResult().success_count > 0) {
      add_buffer_[0] = '\0';
    }
  }

  ImGui::Spacing();
  ImGui::PushItemWidth(ImGui::GetContentRegionAvail().x * 0.7F);
  ImGui::InputTextWithHint("##new_db_name", UIConfig::kNewDbInputHint,
                           new_db_name_buffer_, sizeof(new_db_name_buffer_));
  ImGui::PopItemWidth();
  ImGui::SameLine();
  if (ImGui::Button(UIConfig::kCreateNewDbButton)) {
    app_.PerformCreateDatabase(new_db_name_buffer_);
    UpdateStatusMessage();
    if (app_.GetLastResult() == ResultCode::kDbCreated) {
      new_db_name_buffer_[0] = '\0';
    }
  }

  ImGui::Separator();

  ImGui::Text(UIConfig::kQuerySectionHeader, current_db.c_str());
  ImGui::PushItemWidth(ImGui::GetContentRegionAvail().x * 0.7F);
  if (ImGui::InputText("##query_id", query_buffer_, sizeof(query_buffer_),
                       ImGuiInputTextFlags_EnterReturnsTrue)) {
    app_.PerformQuery(query_buffer_);
    UpdateStatusMessage();
  }
  ImGui::PopItemWidth();
  ImGui::SameLine();
  if (ImGui::Button(UIConfig::kQueryButton)) {
    app_.PerformQuery(query_buffer_);
    UpdateStatusMessage();
  }

  ImGui::Separator();

  ImGui::Text(UIConfig::kImportSectionHeader);
  ImGui::PushItemWidth(ImGui::GetContentRegionAvail().x * 0.7F);
  ImGui::InputTextWithHint("##import_path", UIConfig::kImportInputHint,
                           import_path_buffer_, sizeof(import_path_buffer_));
  ImGui::PopItemWidth();
  ImGui::SameLine();
  if (ImGui::Button(UIConfig::kImportButton)) {
    try {
      IO::TextFileReader reader;
      auto lines = reader.ReadAllLines(import_path_buffer_);
      app_.PerformImportLines(lines);
    } catch (const std::runtime_error&) {
      app_.SetError(ErrorCode::kFileOpenFailed);
    }
    UpdateStatusMessage();
    if (app_.GetLastResult() == ResultCode::kImportCompleted &&
        app_.GetLastImportResult().success_count > 0) {
      import_path_buffer_[0] = '\0';
    }
  }

  ImGui::Separator();

  ImGui::Text(UIConfig::kExportSectionHeader);
  ImGui::PushItemWidth(ImGui::GetContentRegionAvail().x * 0.7F);
  ImGui::InputTextWithHint("##export_path", UIConfig::kExportInputHint,
                           export_path_buffer_, sizeof(export_path_buffer_));
  ImGui::PopItemWidth();
  ImGui::SameLine();
  if (ImGui::Button(UIConfig::kExportButton)) {
    std::string out_path = export_path_buffer_;
    if (out_path.empty()) {
      out_path = (std::filesystem::current_path() / "output.txt").string();
    }
    std::vector<std::string> ids;
    if (app_.FetchAllIds(ids)) {
      std::ofstream out(out_path, std::ios::out | std::ios::trunc);
      if (!out.is_open()) {
        app_.SetError(ErrorCode::kFileOpenFailed);
      } else {
        for (const auto& id : ids) {
          out << id << '\n';
        }
        app_.SetInfoMessage("导出完成，文件路径: " + out_path);
      }
    }
    UpdateStatusMessage();
  }

  ImGui::Separator();

  ImGui::Text(UIConfig::kStatusLabel, status_message_.c_str());
  ImGui::Text(UIConfig::kTotalRecordsLabel, app_.GetTotalRecords());

  auto version_text =
      std::string("Version: ") + std::string(AppVersion::kVersionString);
  auto text_width = ImGui::CalcTextSize(version_text.c_str()).x;
  ImGui::SameLine(ImGui::GetWindowWidth() - text_width -
                  ImGui::GetStyle().WindowPadding.x);
  ImGui::Text("%s", version_text.c_str());

  ImGui::Separator();
  ImGui::Text("字体: %s", UIConfig::kFontPath);
}
