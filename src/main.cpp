#include "App/Application.h"
#include "View/ImGuiView.h"
#include <memory>

int main(int, char**) {
    // 1. 创建应用逻辑层实例
    Application app;

    // 2. 创建一个GUI视图的实现，并把App的引用传给它
    //    如果想换成Qt，只需要改成 std::make_unique<QtView>(app)
    std::unique_ptr<IGuiView> gui = std::make_unique<ImGuiView>(app);

    // 3. 启动GUI
    if (gui->init()) {
        gui->run();
    }
    
    // 4. 程序结束，清理资源
    gui->cleanup();

    return 0;
}