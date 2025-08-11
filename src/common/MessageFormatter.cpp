#include "MessageFormatter.h"
#include "View/ImGui/UIConfig.h" // 关键：包含UI配置头文件以获取消息文本

std::string MessageFormatter::format_message(const Application& app) {
    AppStatus status = app.get_status();
    const auto& result = app.get_operation_result();

    // 所有消息文本都从 UIConfig::Messages 中获取
    switch (status) {
        case AppStatus::Idle:             return std::string(UIConfig::Messages::Idle);
        case AppStatus::Welcome:          return std::string(UIConfig::Messages::Welcome);
        case AppStatus::DBLoadSuccess:    return std::string(UIConfig::Messages::DBLoadSuccess);
        case AppStatus::DBSwitched:       return UIConfig::Messages::dbSwitched(app.get_current_db_name());
        case AppStatus::DBCreated:        return UIConfig::Messages::dbCreated(app.get_current_db_name());
        
        case AppStatus::AddCompleted:     return UIConfig::Messages::addCompleted(result);
        case AppStatus::QueryCompleted:   return UIConfig::Messages::queryCompleted(result);

        case AppStatus::ErrorDBNotExist:  return std::string(UIConfig::Messages::ErrorDBNotExist);
        case AppStatus::ErrorDBCreateFailed: return std::string(UIConfig::Messages::ErrorDBCreateFailed);
        case AppStatus::ErrorDBNameExists: return std::string(UIConfig::Messages::ErrorDBNameExists);
        case AppStatus::ErrorDBNameEmpty: return std::string(UIConfig::Messages::ErrorDBNameEmpty);
        case AppStatus::ErrorAddIDEmpty:  return std::string(UIConfig::Messages::ErrorAddIDEmpty);
        case AppStatus::ErrorQueryIDEmpty: return std::string(UIConfig::Messages::ErrorQueryIDEmpty);
        default:                          return std::string(UIConfig::Messages::UnknownError);
    }
}