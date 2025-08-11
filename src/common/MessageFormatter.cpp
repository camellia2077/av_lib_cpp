#include "MessageFormatter.h"

std::string MessageFormatter::format_message(const Application& app) {
    AppStatus status = app.get_status();
    const auto& result = app.get_operation_result();
    std::string msg;

    switch (status) {
        case AppStatus::Idle:             msg = "准备就绪。"; break;
        case AppStatus::Welcome:          msg = "欢迎使用！"; break;
        case AppStatus::DBLoadSuccess:    msg = "默认数据库加载成功。"; break;
        case AppStatus::DBSwitched:       msg = "已切换到数据库: " + app.get_current_db_name(); break;
        case AppStatus::DBCreated:        msg = "成功创建并切换到数据库: " + app.get_current_db_name(); break;
        
        case AppStatus::AddCompleted:
            msg = "在 [" + result.target_db_name + "] 中添加完成。 ";
            msg += "成功: " + std::to_string(result.success_count) + "个。 ";
            if (result.exist_count > 0) msg += "已存在: " + std::to_string(result.exist_count) + "个。 ";
            if (result.invalid_format_count > 0) msg += "格式错误: " + std::to_string(result.invalid_format_count) + "个。";
            break;

        case AppStatus::QueryCompleted:
            msg = "在 [" + result.target_db_name + "] 中查询完成。 ";
            msg += "找到: " + std::to_string(result.success_count) + "个。 ";
            if (result.not_found_count > 0) msg += "未找到: " + std::to_string(result.not_found_count) + "个。 ";
            if (result.invalid_format_count > 0) msg += "格式错误: " + std::to_string(result.invalid_format_count) + "个。";
            break;

        case AppStatus::ErrorDBNotExist:  msg = "错误：目标数据库不存在。"; break;
        case AppStatus::ErrorDBCreateFailed: msg = "错误：创建数据库文件失败。"; break;
        case AppStatus::ErrorDBNameExists: msg = "错误：该名称的数据库已经存在。"; break;
        case AppStatus::ErrorDBNameEmpty: msg = "错误：新数据库名称不能为空。"; break;
        case AppStatus::ErrorAddIDEmpty:  msg = "错误：不能添加空的内容。"; break;
        case AppStatus::ErrorQueryIDEmpty: msg = "提示：请输入要查询的内容。"; break;
        default: msg = "未知状态。"; break;
    }
    return msg;
}