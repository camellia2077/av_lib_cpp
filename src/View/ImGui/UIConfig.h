#pragma once

#include "App/Application.h" // 包含此文件以使用 OperationResult
#include <string_view>
#include <string> 
// 这个文件现在包含了所有的状态消息文本。MessageFormatter 将从这里读取消息。

// 使用命名空间来组织所有UI相关的配置
namespace UIConfig {
    // --- 字体和窗口配置 ---
    constexpr float DefaultFontSize = 36.0f;
    constexpr const char* FontPath = "fonts/NotoSansSC-Regular.ttf";
    constexpr const char* MainWindowTitle = "查询内容是否重复工具";
    constexpr float CornerRounding = 14.0f;

    // --- 数据库选择区域 ---
    constexpr const char* CurrentDbLabel = "当前数据库选择";

    // --- 内容存入区域 ---
    constexpr const char* AddSectionHeader = "内容存入 (可批量, 用空格隔开)";
    constexpr const char* AddToCurrentDbButton = "添加到当前库";
    constexpr const char* NewDbInputHint = "或输入新库名(如: new_db)";
    constexpr const char* CreateNewDbButton = "创建新的库";
    
    // --- 内容查询区域 ---
    constexpr const char* QuerySectionHeader = "内容查询 (在当前库 '%s' 中查询)";
    constexpr const char* QueryButton = "查询";
    
    // --- 状态栏区域 ---
    constexpr const char* StatusLabel = "状态: %s";
    constexpr const char* TotalRecordsLabel = "当前库记录总数: %zu";

    // --- 新增：统一管理所有状态消息文本 ---
    namespace Messages {
        // --- 通用状态 ---
        constexpr std::string_view Idle = "准备就绪。";
        constexpr std::string_view Welcome = "欢迎使用！";
        constexpr std::string_view DBLoadSuccess = "默认数据库加载成功。";
        constexpr std::string_view UnknownError = "未知状态。";

        // --- 动态生成的消息 ---
        inline std::string dbSwitched(const std::string& db_name) { return "已切换到数据库: " + db_name; }
        inline std::string dbCreated(const std::string& db_name) { return "成功创建并切换到数据库: " + db_name; }
        
        // --- 批量操作结果格式化 ---
        inline std::string addCompleted(const OperationResult& result) {
            std::string msg = "在 [" + result.target_db_name + "] 中添加完成。 ";
            msg += "成功: " + std::to_string(result.success_count) + "个。 ";
            if (result.exist_count > 0) msg += "已存在: " + std::to_string(result.exist_count) + "个。 ";
            if (result.invalid_format_count > 0) msg += "格式错误: " + std::to_string(result.invalid_format_count) + "个。";
            return msg;
        }

        inline std::string queryCompleted(const OperationResult& result) {
            std::string msg = "在 [" + result.target_db_name + "] 中查询完成。 ";
            msg += "找到: " + std::to_string(result.success_count) + "个。 ";
            if (result.not_found_count > 0) msg += "未找到: " + std::to_string(result.not_found_count) + "个。 ";
            if (result.invalid_format_count > 0) msg += "格式错误: " + std::to_string(result.invalid_format_count) + "个。";
            return msg;
        }

        // --- 错误信息 ---
        constexpr std::string_view ErrorDBNotExist = "错误：目标数据库不存在。";
        constexpr std::string_view ErrorDBCreateFailed = "错误：创建数据库文件失败。";
        constexpr std::string_view ErrorDBNameExists = "错误：该名称的数据库已经存在。";
        constexpr std::string_view ErrorDBNameEmpty = "错误：新数据库名称不能为空。";
        constexpr std::string_view ErrorAddIDEmpty = "错误：不能添加空的内容。";
        constexpr std::string_view ErrorQueryIDEmpty = "提示：请输入要查询的内容。";
    }
}