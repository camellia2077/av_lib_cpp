
#include "App/Application.h"
#include <iostream>
#include <limits>
#include <vector>
#include <string>
#include "common/MessageFormatter.h"

#ifdef _WIN32
#include <windows.h>
#endif

/// --- 修改：命令行版本的状态消息处理函数 ---
void print_status_message(Application& app) {
    // 直接调用 MessageFormatter 来获取格式化后的消息
    std::string msg = MessageFormatter::format_message(app);
    std::cout << "结果: " << msg << std::endl;
}

// 菜单函数保持不变
void print_menu(const std::string& current_db) {
    std::cout << "\n--- 命令行查询工具 ---" << std::endl;
    std::cout << "当前数据库: [" << current_db << "]" << std::endl;
    std::cout << "1. 添加内容 (可批量, 用空格隔开)" << std::endl;
    std::cout << "2. 查询内容 (可批量, 用空格隔开)" << std::endl;
    std::cout << "3. 创建新数据库" << std::endl;
    std::cout << "4. 切换数据库" << std::endl;
    std::cout << "5. 查看当前库状态" << std::endl;
    std::cout << "0. 退出" << std::endl;
    std::cout << "请输入选项: ";
}

void clear_cin() {
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
}

int main() {
#ifdef _WIN32
    SetConsoleOutputCP(CP_UTF8);
#endif
    
    Application app;
    app.load_database();
    print_status_message(app); // 初始加载后显示状态

    int choice;
    std::string input_buffer;

    while (true) {
        print_menu(app.get_current_db_name());
        std::cin >> choice;

        if (std::cin.fail()) {
            std::cout << "错误: 无效输入，请输入数字。" << std::endl;
            std::cin.clear();
            clear_cin();
            continue;
        }
        clear_cin(); 

        switch (choice) {
            case 1: // 添加
                std::cout << "输入要添加的内容: ";
                std::getline(std::cin, input_buffer);
                app.perform_add(input_buffer);
                print_status_message(app);
                break;

            case 2: // 查询
                std::cout << "输入要查询的内容: ";
                std::getline(std::cin, input_buffer);
                app.perform_query(input_buffer);
                print_status_message(app);
                break;

            case 3: // 创建数据库
                std::cout << "输入新数据库名称: ";
                std::getline(std::cin, input_buffer);
                app.perform_create_database(input_buffer);
                print_status_message(app);
                break;

            case 4: // 切换数据库
            {
                std::vector<std::string> dbs = app.get_database_names();
                if (dbs.empty()) {
                    std::cout << "当前没有可切换的数据库。" << std::endl;
                    break;
                }
                std::cout << "可用数据库:" << std::endl;
                for (size_t i = 0; i < dbs.size(); ++i) {
                    std::cout << i + 1 << ". " << dbs[i] << std::endl;
                }
                std::cout << "选择要切换的数据库编号: ";
                int db_choice;
                std::cin >> db_choice;
                 if (std::cin.fail() || db_choice < 1 || db_choice > dbs.size()) {
                    std::cout << "错误: 无效选择。" << std::endl;
                    std::cin.clear();
                    clear_cin();
                    break;
                }
                clear_cin();
                app.set_current_database(dbs[db_choice - 1]);
                print_status_message(app);
                break;
            }

            case 5: // 查看状态
                std::cout << "当前库记录总数: " << app.get_total_records() << std::endl;
                break;

            case 0: // 退出
                std::cout << "程序退出。" << std::endl;
                return 0;

            default:
                std::cout << "无效选项，请重试。" << std::endl;
                break;
        }
    }

    return 0;
}