#pragma once

#include <string_view>

// 使用命名空间来组织所有UI相关的配置
namespace UIConfig {
    // --- 字体和窗口配置 ---
    constexpr float DefaultFontSize = 36.0f;
    constexpr const char* FontPath = "fonts/NotoSansSC-Regular.ttf";
    constexpr const char* MainWindowTitle = "查询av是否重复工具";
    constexpr float CornerRounding = 14.0f; // 圆角半径配置在此处

    // --- 通用信息文本 ---
    constexpr std::string_view Welcome = "欢迎使用! 请操作.";
    // ... (文件其余部分保持不变)
    constexpr std::string_view DBLoadSuccess = "默认数据库加载成功.";

    // --- 数据库选择区域 ---
    constexpr const char* CurrentDbLabel = "当前数据库选择";

    // --- 编号存入区域 ---
    constexpr const char* AddSectionHeader = "编号存入 (可批量, 用空格隔开)";
    constexpr const char* AddToCurrentDbButton = "添加到当前库";
    constexpr const char* NewDbInputHint = "或输入新库名(如: new_db)";
    constexpr const char* CreateNewDbButton = "创建新的库";
    
    // --- 编号查询区域 ---
    // 注意: %s 是一个占位符，使用时需要格式化字符串
    constexpr const char* QuerySectionHeader = "编号查询 (在当前库 '%s' 中查询)";
    constexpr const char* QueryButton = "查询";
    
    // --- 状态栏区域 ---
    // 注意: %s 和 %zu 是占位符
    constexpr const char* StatusLabel = "状态: %s";
    constexpr const char* TotalRecordsLabel = "当前库记录总数: %zu";
    
    // --- 操作结果与错误信息 (来自原 UIText.h) ---
    constexpr std::string_view InfoAddSuccess = "成功添加: ";
    constexpr std::string_view ErrorAddEmptyID = "错误: 不能添加空的ID.";
    constexpr std::string_view ErrorIDExistsPart1 = "错误: ID '";
    constexpr std::string_view ErrorIDExistsPart2 = "' 已存在.";
    constexpr std::string_view InfoQueryPrompt = "提示: 请输入要查询的ID.";
    constexpr std::string_view ResultIDFoundPart1 = "结果: ID '";
    constexpr std::string_view ResultIDFoundPart2 = "' 已找到.";
    constexpr std::string_view ResultIDNotFoundPart1 = "结果: ID '";
    constexpr std::string_view ResultIDNotFoundPart2 = "' 不存在.";
}