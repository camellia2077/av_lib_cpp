// apps/cli/cli_presenter.hpp
#ifndef CLI_PRESENTER_HPP
#define CLI_PRESENTER_HPP

#include <string>

#include "apps/cli/cli_config.hpp"
#include "core/app/application.hpp"

class CLIPresenter {
 public:
  static auto Format(const Application& app) -> std::string {
    if (!app.GetInfoMessage().empty()) {
      return app.GetInfoMessage();
    }
    if (app.GetLastError() != ErrorCode::kNone) {
      switch (app.GetLastError()) {
        case ErrorCode::kDbNotExist:
          return std::string(CLIConfig::Messages::kErrorDbNotExist);
        case ErrorCode::kDbCreateFailed:
          return std::string(CLIConfig::Messages::kErrorDbCreateFailed);
        case ErrorCode::kDbNameExists:
          return std::string(CLIConfig::Messages::kErrorDbNameExists);
        case ErrorCode::kDbNameEmpty:
          return std::string(CLIConfig::Messages::kErrorDbNameEmpty);
        case ErrorCode::kAddIdEmpty:
          return std::string(CLIConfig::Messages::kErrorAddIdEmpty);
        case ErrorCode::kQueryIdEmpty:
          return std::string(CLIConfig::Messages::kErrorQueryIdEmpty);
        case ErrorCode::kIdInvalid:
          return std::string(CLIConfig::Messages::kErrorIdInvalid);
        case ErrorCode::kFileOpenFailed:
          return std::string(CLIConfig::Messages::kErrorFileOpenFailed);
        case ErrorCode::kFileEmpty:
          return std::string(CLIConfig::Messages::kErrorFileEmpty);
        case ErrorCode::kNone:
          return std::string(CLIConfig::Messages::kUnknownError);
      }
    }

    switch (app.GetLastResult()) {
      case ResultCode::kIdle:
        return std::string(CLIConfig::Messages::kIdle);
      case ResultCode::kWelcome:
        return std::string(CLIConfig::Messages::kWelcome);
      case ResultCode::kDbLoadSuccess:
        return std::string(CLIConfig::Messages::kDbLoadSuccess);
      case ResultCode::kDbSwitched:
        return CLIConfig::Messages::DbSwitched(app.GetCurrentDbName());
      case ResultCode::kDbCreated:
        return CLIConfig::Messages::DbCreated(app.GetCurrentDbName());
      case ResultCode::kAddCompleted:
        return CLIConfig::Messages::AddCompleted(app.GetLastAddResult());
      case ResultCode::kQueryCompleted:
        return CLIConfig::Messages::QueryCompleted(app.GetLastQueryResult());
      case ResultCode::kImportCompleted:
        return CLIConfig::Messages::ImportCompleted(app.GetLastImportResult());
    }

    return std::string(CLIConfig::Messages::kUnknownError);
  }
};

#endif

