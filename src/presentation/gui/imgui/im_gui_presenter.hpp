// view/imgui/im_gui_presenter.hpp
#ifndef IM_GUI_PRESENTER_HPP
#define IM_GUI_PRESENTER_HPP

#include <string>

#include "core/app/application.hpp"
#include "presentation/gui/imgui/impl/ui_config.hpp"

class ImGuiPresenter {
 public:
  static auto Format(const Application& app) -> std::string {
    if (!app.GetInfoMessage().empty()) {
      return app.GetInfoMessage();
    }
    if (app.GetLastError() != ErrorCode::kNone) {
      switch (app.GetLastError()) {
        case ErrorCode::kDbNotExist:
          return std::string(UIConfig::Messages::kErrorDbNotExist);
        case ErrorCode::kDbCreateFailed:
          return std::string(UIConfig::Messages::kErrorDbCreateFailed);
        case ErrorCode::kDbNameExists:
          return std::string(UIConfig::Messages::kErrorDbNameExists);
        case ErrorCode::kDbNameEmpty:
          return std::string(UIConfig::Messages::kErrorDbNameEmpty);
        case ErrorCode::kAddIdEmpty:
          return std::string(UIConfig::Messages::kErrorAddIdEmpty);
        case ErrorCode::kQueryIdEmpty:
          return std::string(UIConfig::Messages::kErrorQueryIdEmpty);
        case ErrorCode::kIdInvalid:
          return std::string(UIConfig::Messages::kErrorIdInvalid);
        case ErrorCode::kFileOpenFailed:
          return std::string(UIConfig::Messages::kErrorFileOpenFailed);
        case ErrorCode::kFileEmpty:
          return std::string(UIConfig::Messages::kErrorFileEmpty);
        case ErrorCode::kNone:
          return std::string(UIConfig::Messages::kUnknownError);
      }
    }

    switch (app.GetLastResult()) {
      case ResultCode::kIdle:
        return std::string(UIConfig::Messages::kIdle);
      case ResultCode::kWelcome:
        return std::string(UIConfig::Messages::kWelcome);
      case ResultCode::kDbLoadSuccess:
        return std::string(UIConfig::Messages::kDbLoadSuccess);
      case ResultCode::kDbSwitched:
        return UIConfig::Messages::DbSwitched(app.GetCurrentDbName());
      case ResultCode::kDbCreated:
        return UIConfig::Messages::DbCreated(app.GetCurrentDbName());
      case ResultCode::kAddCompleted:
        return UIConfig::Messages::AddCompleted(app.GetLastAddResult());
      case ResultCode::kQueryCompleted:
        return UIConfig::Messages::QueryCompleted(app.GetLastQueryResult());
      case ResultCode::kImportCompleted:
        return UIConfig::Messages::ImportCompleted(app.GetLastImportResult());
    }

    return std::string(UIConfig::Messages::kUnknownError);
  }
};

#endif
