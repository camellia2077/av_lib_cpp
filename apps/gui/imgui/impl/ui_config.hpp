// apps/gui/imgui/impl/ui_config.hpp
#ifndef U_I_CONFIG_HPP
#define U_I_CONFIG_HPP

#include <string>
#include <string_view>

#include "core/app/application.hpp"  // 包含此文件以使用结果模型
// 这个文件现在包含了所有的状态消息文本。

// 使用命名空间来组织所有UI相关的配置
namespace UIConfig {
// --- 字体和窗口配置 ---
constexpr float kDefaultFontSize = 36.0F;
constexpr const char* kFontPath = "fonts/NotoSansSC-Regular.ttf";
constexpr const char* kMainWindowTitle = "查询内容是否重复工具";
constexpr float kCornerRounding = 14.0F;

// --- 数据库选择区域 ---
constexpr const char* kCurrentDbLabel = "当前数据库选择";

// --- 内容存入区域 ---
constexpr const char* kAddSectionHeader = "内容存入 (可批量, 用空格隔开)";
constexpr const char* kAddToCurrentDbButton = "添加到当前库";
constexpr const char* kNewDbInputHint = "或输入新库名(如: new_db)";
constexpr const char* kCreateNewDbButton = "创建新的库";

// --- 内容查询区域 ---
constexpr const char* kQuerySectionHeader = "内容查询 (在当前库 '%s' 中查询)";
constexpr const char* kQueryButton = "查询";

// --- 导入区域 ---
constexpr const char* kImportSectionHeader = "从 .txt 文件导入到当前库";
constexpr const char* kImportInputHint = "输入 .txt 路径";
constexpr const char* kImportButton = "导入";

// --- 导出区域 ---
constexpr const char* kExportSectionHeader = "导出当前库到 .txt";
constexpr const char* kExportInputHint = "输出路径(留空则output.txt)";
constexpr const char* kExportButton = "导出";

// --- 状态栏区域 ---
constexpr const char* kStatusLabel = "状态: %s";
constexpr const char* kTotalRecordsLabel = "当前库记录总数: %zu";

// --- 新增：统一管理所有状态消息文本 ---
namespace Messages {
// --- 通用状态 ---
constexpr std::string_view kIdle = "准备就绪。";
constexpr std::string_view kWelcome = "欢迎使用！";
constexpr std::string_view kDbLoadSuccess = "默认数据库加载成功。";
constexpr std::string_view kUnknownError = "未知状态。";

// --- 动态生成的消息 ---
inline auto DbSwitched(const std::string& db_name) -> std::string {
  return "已切换到数据库: " + db_name;
}
inline auto DbCreated(const std::string& db_name) -> std::string {
  return "成功创建并切换到数据库: " + db_name;
}

// --- 批量操作结果格式化 ---
inline auto AddCompleted(const AddResult& result) -> std::string {
  std::string msg = "在 [" + result.target_db_name + "] 中添加完成。 ";
  msg += "成功: " + std::to_string(result.success_count) + "个。 ";
  if (result.exist_count > 0) {
    msg += "已存在: " + std::to_string(result.exist_count) + "个。 ";
  }
  if (result.invalid_format_count > 0) {
    msg += "格式错误: " + std::to_string(result.invalid_format_count) + "个。";
  }
  return msg;
}

inline auto QueryCompleted(const QueryResult& result) -> std::string {
  std::string msg = "在 [" + result.target_db_name + "] 中查询完成。 ";
  msg += "找到: " + std::to_string(result.found_count) + "个。 ";
  if (result.not_found_count > 0) {
    msg += "未找到: " + std::to_string(result.not_found_count) + "个。 ";
  }
  if (result.invalid_format_count > 0) {
    msg += "格式错误: " + std::to_string(result.invalid_format_count) + "个。";
  }
  return msg;
}

// --- 错误信息 ---
constexpr std::string_view kErrorDbNotExist = "错误：目标数据库不存在。";
constexpr std::string_view kErrorDbCreateFailed = "错误：创建数据库文件失败。";
constexpr std::string_view kErrorDbNameExists =
    "错误：该名称的数据库已经存在。";
constexpr std::string_view kErrorDbNameEmpty = "错误：新数据库名称不能为空。";
constexpr std::string_view kErrorAddIdEmpty = "错误：不能添加空的内容。";
constexpr std::string_view kErrorQueryIdEmpty = "提示：请输入要查询的内容。";
constexpr std::string_view kErrorIdInvalid =
    "错误：无效的选项或格式。";  // --- [ADD THIS LINE] ---

inline auto ImportCompleted(const ImportResult& result) -> std::string {
  std::string msg = "从文件导入到 [" + result.target_db_name + "] 完成。 ";
  msg += "成功: " + std::to_string(result.success_count) + "。 ";
  if (result.exist_count > 0) {
    msg += "已存在: " + std::to_string(result.exist_count) + "。 ";
  }
  if (result.invalid_format_count > 0) {
    msg += "格式错误: " + std::to_string(result.invalid_format_count) + "。";
  }
  return msg;
}
constexpr std::string_view kErrorFileOpenFailed = "错误：无法打开指定的文件。";
constexpr std::string_view kErrorFileEmpty = "提示：文件为空或只包含空行。";
}  // namespace Messages
}  // namespace UIConfig
#endif

