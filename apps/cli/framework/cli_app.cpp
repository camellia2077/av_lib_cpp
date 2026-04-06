// apps/cli/framework/cli_app.cpp
#include "apps/cli/framework/cli_app.hpp"

#include <cstdlib>
#include <iostream>
#include <limits>

#include "apps/cli/cli_presenter.hpp"

#ifdef _WIN32
#include <windows.h>
#endif

CLIApp::CLIApp(Application& app) : app_(app), commands_(app) {}

void CLIApp::clear_screen() {
#ifdef _WIN32
  system("cls");
#else
  system("clear");
#endif
}

void CLIApp::print_status_message() {
  std::string msg = CLIPresenter::Format(app_);
  std::cout << "结果: " << msg << std::endl;
}

void CLIApp::print_menu(const std::string& current_db) {
  std::cout << "\n--- 命令行查询工具 ---" << std::endl;
  std::cout << "当前数据库: [" << current_db << "]" << std::endl;
  std::cout << "1. 添加内容 (可批量, 用空格隔开)" << std::endl;
  std::cout << "2. 查询内容 (可批量, 用空格隔开)" << std::endl;
  std::cout << "3. 创建新数据库" << std::endl;
  std::cout << "4. 切换数据库" << std::endl;
  std::cout << "5. 从 .txt 文件批量导入" << std::endl;
  std::cout << "6. 查看当前库状态" << std::endl;
  std::cout << "7. 查看当前版本" << std::endl;
  std::cout << "8. 导出当前库到 .txt" << std::endl;
  std::cout << "0. 退出" << std::endl;
  std::cout << "请输入选项: ";
}

void CLIApp::clear_cin() {
  std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
}

void CLIApp::Run() {
#ifdef _WIN32
  SetConsoleOutputCP(CP_UTF8);
#endif

  app_.LoadDatabase();

  int choice;
  std::string input_buffer;

  while (true) {
    clear_screen();
    print_status_message();
    print_menu(app_.GetCurrentDbName());

    std::cin >> choice;

    if (std::cin.fail()) {
      clear_screen();
      std::cout << "错误: 无效输入，请输入数字。" << std::endl;
      std::cin.clear();
      clear_cin();
      continue;
    }
    clear_cin();

    switch (choice) {
      case 1:
        std::cout << "输入要添加的内容: ";
        std::getline(std::cin, input_buffer);
        commands_.AddIds(input_buffer);
        break;
      case 2:
        std::cout << "输入要查询的内容: ";
        std::getline(std::cin, input_buffer);
        commands_.QueryId(input_buffer);
        break;
      case 3:
        std::cout << "输入新数据库名称: ";
        std::getline(std::cin, input_buffer);
        commands_.CreateDatabase(input_buffer);
        break;
      case 4:
        commands_.SwitchDatabase();
        break;
      case 5:
        std::cout << "输入 .txt 文件路径: ";
        std::getline(std::cin, input_buffer);
        commands_.ImportFromFile(input_buffer);
        break;
      case 6:
        clear_screen();
        commands_.ShowStatus();
        break;
      case 7:
        clear_screen();
        commands_.ShowVersion();
        break;
      case 8:
        std::cout << "输出 .txt 文件路径: ";
        std::getline(std::cin, input_buffer);
        commands_.ExportToFile(input_buffer);
        break;
      case 0:
        clear_screen();
        std::cout << "程序退出。" << std::endl;
        return;
      default:
        app_.SetError(ErrorCode::kIdInvalid);
        break;
    }
  }
}

