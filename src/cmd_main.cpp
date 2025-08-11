#include "App/Application.h"
#include <iostream>
#include <limits>
#include <vector>
#include <string>

#ifdef _WIN32
#include <windows.h>
#endif

// --- 新增：命令行版本的状态消息处理函数 ---
// 它将AppStatus和OperationResult翻译成可读的文本
void print_status_message(Application& app) {
    AppStatus status = app.get_status();
    const auto& result = app.get_operation_result();
    std::string msg;

    switch (status) {
        case AppStatus::Idle:             msg = "准备就绪。"; break;
        case AppStatus::Welcome:          msg = "欢迎使用命令行工具！"; break;
        case AppStatus::DBLoadSuccess:    msg = "默认数据库加载成功。"; break;
        case AppStatus::DBSwitched:       msg = "已切换到数据库: " + app.get_current_db_name(); break;
        case AppStatus::DBCreated:        msg = "成功创建并切换到数据库: " + app.get_current_db_name(); break;
        
        case AppStatus::AddCompleted:
            msg = "在 [" + result.target_db_name + "] 中添加完成。 ";
            msg += "成功: " + std::to_string(result.success_count) + "个。 ";
            if (result.exist_count > 0) msg += "已存在: " + std::to_string(result.exist_count) + "个。 ";
            if (result.invalid_format_count > 0) msg += "格式错误: " + std::to_string(result.invalid_format_count) + "个。";
            break;

        case AppStatus::QueryCompleted:
            msg = "在 [" + result.target_db_name + "] 中查询完成。 ";
            msg += "找到: " + std::to_string(result.success_count) + "个。 ";
            if (result.not_found_count > 0) msg += "未找到: " + std::to_string(result.not_found_count) + "个。 ";
            if (result.invalid_format_count > 0) msg += "格式错误: " + std::to_string(result.invalid_format_count) + "个。";
            break;

        case AppStatus::ErrorDBNotExist:  msg = "错误：目标数据库不存在。"; break;
        case AppStatus::ErrorDBCreateFailed: msg = "错误：创建数据库文件失败。"; break;
        case AppStatus::ErrorDBNameExists: msg = "错误：该名称的数据库已经存在。"; break;
        case AppStatus::ErrorDBNameEmpty: msg = "错误：新数据库名称不能为空。"; break;
        case AppStatus::ErrorAddIDEmpty:  msg = "错误：不能添加空的内容。"; break;
        case AppStatus::ErrorQueryIDEmpty: msg = "提示：请输入要查询的内容。"; break;
        default: msg = "未知状态。"; break;
    }
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