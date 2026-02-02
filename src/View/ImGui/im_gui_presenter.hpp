// view/imgui/im_gui_presenter.hpp
#ifndef IM_GUI_PRESENTER_HPP
#define IM_GUI_PRESENTER_HPP

#include "app/application.hpp"
#include "view/imgui/impl/ui_config.hpp"
#include <string>

class ImGuiPresenter {
public:
  static std::string format(const Application &app) {
    if (!app.get_info_message().empty()) {
      return app.get_info_message();
    }
    if (app.get_last_error() != ErrorCode::None) {
      switch (app.get_last_error()) {
      case ErrorCode::DBNotExist:
        return std::string(UIConfig::Messages::ErrorDBNotExist);
      case ErrorCode::DBCreateFailed:
        return std::string(UIConfig::Messages::ErrorDBCreateFailed);
      case ErrorCode::DBNameExists:
        return std::string(UIConfig::Messages::ErrorDBNameExists);
      case ErrorCode::DBNameEmpty:
        return std::string(UIConfig::Messages::ErrorDBNameEmpty);
      case ErrorCode::AddIDEmpty:
        return std::string(UIConfig::Messages::ErrorAddIDEmpty);
      case ErrorCode::QueryIDEmpty:
        return std::string(UIConfig::Messages::ErrorQueryIDEmpty);
      case ErrorCode::IdInvalid:
        return std::string(UIConfig::Messages::ErrorIdInvalid);
      case ErrorCode::FileOpenFailed:
        return std::string(UIConfig::Messages::ErrorFileOpenFailed);
      case ErrorCode::FileEmpty:
        return std::string(UIConfig::Messages::ErrorFileEmpty);
      case ErrorCode::None:
        return std::string(UIConfig::Messages::UnknownError);
      }
    }

    switch (app.get_last_result()) {
    case ResultCode::Idle:
      return std::string(UIConfig::Messages::Idle);
    case ResultCode::Welcome:
      return std::string(UIConfig::Messages::Welcome);
    case ResultCode::DBLoadSuccess:
      return std::string(UIConfig::Messages::DBLoadSuccess);
    case ResultCode::DBSwitched:
      return UIConfig::Messages::dbSwitched(app.get_current_db_name());
    case ResultCode::DBCreated:
      return UIConfig::Messages::dbCreated(app.get_current_db_name());
    case ResultCode::AddCompleted:
      return UIConfig::Messages::addCompleted(app.get_last_add_result());
    case ResultCode::QueryCompleted:
      return UIConfig::Messages::queryCompleted(app.get_last_query_result());
    case ResultCode::ImportCompleted:
      return UIConfig::Messages::importCompleted(app.get_last_import_result());
    }

    return std::string(UIConfig::Messages::UnknownError);
  }
};

#endif
