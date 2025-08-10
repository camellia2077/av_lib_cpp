#include "App/Application.h"
#include <iostream>
#include <limits>
#include <vector>

// [新增] 包含 Windows 头文件以使用其 API
#ifdef _WIN32
#include <windows.h>
#endif

// Function to print the main menu
void print_menu(const std::string& current_db) {
    std::cout << "\n--- Command-Line Query Tool ---" << std::endl;
    std::cout << "Current Database: [" << current_db << "]" << std::endl;
    std::cout << "1. Add new ID(s) (batch supported, separate with spaces)" << std::endl;
    std::cout << "2. Query ID(s) (batch supported, separate with spaces)" << std::endl;
    std::cout << "3. Create a new database" << std::endl;
    std::cout << "4. Switch database" << std::endl;
    std::cout << "5. Check current database status" << std::endl;
    std::cout << "0. Exit" << std::endl;
    std::cout << "Enter your choice: ";
}

// Function to clear the input buffer, preventing issues with std::getline
void clear_cin() {
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
}
int main() {
    // [新增] 在程序开始时设置控制台输出为 UTF-8
    // 这是保证在 Windows 上正确显示多语言字符的关键
#ifdef _WIN32
    SetConsoleOutputCP(CP_UTF8);
#endif
    // 1. Create an instance of the application logic, same as the GUI version
    Application app;
    app.load_database(); // Load the default database
    std::cout << app.get_status_message() << std::endl;

    int choice;
    std::string input_buffer;

    while (true) {
        print_menu(app.get_current_db_name());
        std::cin >> choice;

        // Handle non-numeric input error and retry
        if (std::cin.fail()) {
            std::cout << "Error: Invalid input. Please enter a number." << std::endl;
            std::cin.clear();
            clear_cin();
            continue;
        }

        clear_cin(); // Clear the newline character left by std::cin

        switch (choice) {
            case 1: // Add
                std::cout << "Enter ID(s) to add: ";
                std::getline(std::cin, input_buffer);
                app.set_add_buffer(input_buffer.c_str());
                app.perform_add();
                std::cout << "Result: " << app.get_status_message() << std::endl;
                break;
            case 2: // Query
                std::cout << "Enter ID(s) to query: ";
                std::getline(std::cin, input_buffer);
                app.set_query_buffer(input_buffer.c_str());
                app.perform_query();
                std::cout << "Result: " << app.get_status_message() << std::endl;
                break;
            case 3: // Create database
                std::cout << "Enter the new database name: ";
                std::getline(std::cin, input_buffer);
                app.set_new_db_name_buffer(input_buffer.c_str());
                app.perform_create_database();
                std::cout << "Result: " << app.get_status_message() << std::endl;
                break;
            case 4: // Switch database
            {
                std::vector<std::string> dbs = app.get_database_names();
                if (dbs.empty()) {
                    std::cout << "No databases available to switch to." << std::endl;
                    break;
                }
                std::cout << "Available databases:" << std::endl;
                for (size_t i = 0; i < dbs.size(); ++i) {
                    std::cout << i + 1 << ". " << dbs[i] << std::endl;
                }
                std::cout << "Select a database number to switch to: ";
                int db_choice;
                std::cin >> db_choice;
                 if (std::cin.fail() || db_choice < 1 || db_choice > dbs.size()) {
                    std::cout << "Error: Invalid selection." << std::endl;
                    std::cin.clear();
                    clear_cin();
                    break;
                }
                app.set_current_database(dbs[db_choice - 1]);
                std::cout << "Result: " << app.get_status_message() << std::endl;
                break;
            }
            case 5: // Check status
                std::cout << "Status: " << app.get_status_message() << std::endl;
                std::cout << "Total records in current DB: " << app.get_total_records() << std::endl;
                break;

            case 0: // Exit
                std::cout << "Exiting program." << std::endl;
                return 0;
            default:
                std::cout << "Invalid choice, please try again." << std::endl;
                break;
        }
    }

    return 0;
}