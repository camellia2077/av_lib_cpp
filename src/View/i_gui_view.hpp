// view/i_gui_view.hpp
#ifndef I_GUI_VIEW_HPP
#define I_GUI_VIEW_HPP

#include <memory>

#include "app/application.hpp"

// 任何GUI实现都必须遵循这个接口
class IGuiView {
 public:
  virtual ~IGuiView() = default;

  // 初始化窗口和GUI环境
  virtual auto Init() -> bool = 0;
  // 运行主循环
  virtual void Run() = 0;
  // 清理资源
  virtual void Cleanup() = 0;
};
#endif