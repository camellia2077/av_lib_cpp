// View/IGuiView.hpp
#ifndef IGUIVIEW_HPP
#define IGUIVIEW_HPP

#include "App/Application.hpp"
#include <memory>

// 任何GUI实现都必须遵循这个接口
class IGuiView {
public:
    virtual ~IGuiView() = default;

    // 初始化窗口和GUI环境
    virtual bool init() = 0;
    // 运行主循环
    virtual void run() = 0;
    // 清理资源
    virtual void cleanup() = 0;
};
#endif