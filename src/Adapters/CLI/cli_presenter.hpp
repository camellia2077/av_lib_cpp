// adapters/cli/cli_presenter.hpp
#ifndef CLI_PRESENTER_HPP
#define CLI_PRESENTER_HPP

#include "adapters/cli/cli_config.hpp"
#include "app/application.hpp"
#include <string>

class CLIPresenter {
public:
  static std::string format(const Application &app) {
    if (!app.get_info_message().empty()) {
      return app.get_info_message();
    }
    if (app.get_last_error() != ErrorCode::None) {
      switch (app.get_last_error()) {
      case ErrorCode::DBNotExist:
        return std::string(CLIConfig::Messages::ErrorDBNotExist);
      case ErrorCode::DBCreateFailed:
        return std::string(CLIConfig::Messages::ErrorDBCreateFailed);
      case ErrorCode::DBNameExists:
        return std::string(CLIConfig::Messages::ErrorDBNameExists);
      case ErrorCode::DBNameEmpty:
        return std::string(CLIConfig::Messages::ErrorDBNameEmpty);
      case ErrorCode::AddIDEmpty:
        return std::string(CLIConfig::Messages::ErrorAddIDEmpty);
      case ErrorCode::QueryIDEmpty:
        return std::string(CLIConfig::Messages::ErrorQueryIDEmpty);
      case ErrorCode::IdInvalid:
        return std::string(CLIConfig::Messages::ErrorIdInvalid);
      case ErrorCode::FileOpenFailed:
        return std::string(CLIConfig::Messages::ErrorFileOpenFailed);
      case ErrorCode::FileEmpty:
        return std::string(CLIConfig::Messages::ErrorFileEmpty);
      case ErrorCode::None:
        return std::string(CLIConfig::Messages::UnknownError);
      }
    }

    switch (app.get_last_result()) {
    case ResultCode::Idle:
      return std::string(CLIConfig::Messages::Idle);
    case ResultCode::Welcome:
      return std::string(CLIConfig::Messages::Welcome);
    case ResultCode::DBLoadSuccess:
      return std::string(CLIConfig::Messages::DBLoadSuccess);
    case ResultCode::DBSwitched:
      return CLIConfig::Messages::dbSwitched(app.get_current_db_name());
    case ResultCode::DBCreated:
      return CLIConfig::Messages::dbCreated(app.get_current_db_name());
    case ResultCode::AddCompleted:
      return CLIConfig::Messages::addCompleted(app.get_last_add_result());
    case ResultCode::QueryCompleted:
      return CLIConfig::Messages::queryCompleted(app.get_last_query_result());
    case ResultCode::ImportCompleted:
      return CLIConfig::Messages::importCompleted(app.get_last_import_result());
    }

    return std::string(CLIConfig::Messages::UnknownError);
  }
};

#endif
