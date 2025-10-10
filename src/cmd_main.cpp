// cmd_main.cpp
#include "App/Application.hpp"
#include <iostream>
#include <limits>
#include <vector>
#include <string>
#include "common/MessageFormatter.hpp"
#include <cstdlib>

#ifdef _WIN32
#include <windows.h>
#endif

void clear_screen() {
#ifdef _WIN32
    system("cls");
#else
    system("clear");
#endif
}

void print_status_message(Application& app) {
    std::string msg = MessageFormatter::format_message(app);
    std::cout << "结果: " << msg << std::endl;
}

void print_menu(const std::string& current_db) {
    std::cout << "\n--- 命令行查询工具 ---" << std::endl;
    std::cout << "当前数据库: [" << current_db << "]" << std::endl;
    std::cout << "1. 添加内容 (可批量, 用空格隔开)" << std::endl;
    std::cout << "2. 查询内容 (可批量, 用空格隔开)" << std::endl;
    std::cout << "3. 创建新数据库" << std::endl;
    std::cout << "4. 切换数据库" << std::endl;
    std::cout << "5. 从 .txt 文件批量导入" << std::endl;
    std::cout << "6. 查看当前库状态" << std::endl;
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

    int choice;
    std::string input_buffer;

    while (true) {
        // --- [核心修改] ---
        // 1. 清空屏幕
        clear_screen();
        // 2. 打印上一次操作的状态/结果
        print_status_message(app);
        // 3. 打印新菜单
        print_menu(app.get_current_db_name());
        
        std::cin >> choice;

        if (std::cin.fail()) {
            // 对于无效输入，我们立即刷新并显示错误
            clear_screen();
            std::cout << "错误: 无效输入，请输入数字。" << std::endl;
            std::cin.clear();
            clear_cin();
            // 在下一次循环开始时，会重新显示菜单
            continue;
        }
        clear_cin(); 
        
        switch (choice) {
            case 1:
                std::cout << "输入要添加的内容: ";
                std::getline(std::cin, input_buffer);
                app.perform_add(input_buffer);
                break;

            case 2:
                std::cout << "输入要查询的内容: ";
                std::getline(std::cin, input_buffer);
                app.perform_query(input_buffer);
                break;

            case 3:
                std::cout << "输入新数据库名称: ";
                std::getline(std::cin, input_buffer);
                app.perform_create_database(input_buffer);
                break;

            case 4:
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
                 if (std::cin.fail() || db_choice < 1 || db_choice > static_cast<int>(dbs.size())) {
                    app.set_status(AppStatus::ErrorIdInvalid); // 设置一个通用错误状态
                    std::cin.clear();
                    clear_cin();
                    break;
                }
                clear_cin();
                app.set_current_database(dbs[db_choice - 1]);
                break;
            }

            case 5:
                std::cout << "输入 .txt 文件路径: ";
                std::getline(std::cin, input_buffer);
                app.perform_import_from_file(input_buffer);
                break;

            case 6:
                // 对于这种只显示信息的操作，我们直接输出
                clear_screen();
                std::cout << "当前库记录总数: " << app.get_total_records() << std::endl;
                std::cout << "\n按回车键返回菜单...";
                std::cin.get(); // 等待用户按键
                break;

            case 0:
                clear_screen();
                std::cout << "程序退出。" << std::endl;
                return 0;

            default:
                app.set_status(AppStatus::ErrorIdInvalid); // 设置一个通用错误状态
                break;
        }
    }

    return 0;
}