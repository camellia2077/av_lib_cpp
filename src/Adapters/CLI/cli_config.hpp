// adapters/cli/cli_config.hpp
#ifndef CLI_CONFIG_HPP
#define CLI_CONFIG_HPP

#include "app/application.hpp"
#include <string>
#include <string_view>

namespace CLIConfig {
namespace Messages {
// --- Generic status messages ---
constexpr std::string_view Idle = "准备就绪。";
constexpr std::string_view Welcome = "欢迎使用！";
constexpr std::string_view DBLoadSuccess = "默认数据库加载成功。";
constexpr std::string_view UnknownError = "未知状态。";

inline std::string dbSwitched(const std::string &db_name) {
  return "已切换到数据库: " + db_name;
}
inline std::string dbCreated(const std::string &db_name) {
  return "成功创建并切换到数据库: " + db_name;
}

inline std::string addCompleted(const AddResult &result) {
  std::string msg = "在 [" + result.target_db_name + "] 中添加完成。 ";
  msg += "成功: " + std::to_string(result.success_count) + "个。 ";
  if (result.exist_count > 0)
    msg += "已存在: " + std::to_string(result.exist_count) + "个。 ";
  if (result.invalid_format_count > 0)
    msg += "格式错误: " + std::to_string(result.invalid_format_count) + "个。";
  return msg;
}

inline std::string queryCompleted(const QueryResult &result) {
  std::string msg = "在 [" + result.target_db_name + "] 中查询完成。 ";
  msg += "找到: " + std::to_string(result.found_count) + "个。 ";
  if (result.not_found_count > 0)
    msg += "未找到: " + std::to_string(result.not_found_count) + "个。 ";
  if (result.invalid_format_count > 0)
    msg += "格式错误: " + std::to_string(result.invalid_format_count) + "个。";
  return msg;
}

inline std::string importCompleted(const ImportResult &result) {
  std::string msg = "从文件导入到 [" + result.target_db_name + "] 完成。 ";
  msg += "成功: " + std::to_string(result.success_count) + "。 ";
  if (result.exist_count > 0)
    msg += "已存在: " + std::to_string(result.exist_count) + "。 ";
  if (result.invalid_format_count > 0)
    msg += "格式错误: " + std::to_string(result.invalid_format_count) + "。";
  return msg;
}

// --- Error messages ---
constexpr std::string_view ErrorDBNotExist = "错误：目标数据库不存在。";
constexpr std::string_view ErrorDBCreateFailed = "错误：创建数据库文件失败。";
constexpr std::string_view ErrorDBNameExists = "错误：该名称的数据库已经存在。";
constexpr std::string_view ErrorDBNameEmpty = "错误：新数据库名称不能为空。";
constexpr std::string_view ErrorAddIDEmpty = "错误：不能添加空的内容。";
constexpr std::string_view ErrorQueryIDEmpty = "提示：请输入要查询的内容。";
constexpr std::string_view ErrorIdInvalid = "错误：无效的选项或格式。";
constexpr std::string_view ErrorFileOpenFailed = "错误：无法打开指定的文件。";
constexpr std::string_view ErrorFileEmpty = "提示：文件为空或只包含空行。";
} // namespace Messages
} // namespace CLIConfig

#endif
