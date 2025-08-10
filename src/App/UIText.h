#pragma once

#include <string_view>

// 使用命名空间来组织所有UI文本，避免污染全局命名空间
namespace UIText {
    // 使用 std::string_view 作为字符串字面量的类型，它高效且不涉及内存分配
    
    // 通用信息
    constexpr std::string_view Welcome = "Welcome! Please load the database.";
    constexpr std::string_view DBLoadSuccess = "Database loaded successfully.";
    
    // 添加操作相关文本
    constexpr std::string_view InfoAddSuccess = "Successfully added: ";
    constexpr std::string_view ErrorAddEmptyID = "Error: Cannot add an empty ID.";
    constexpr std::string_view ErrorIDExistsPart1 = "Error: ID '";
    constexpr std::string_view ErrorIDExistsPart2 = "' already exists.";

    // 查询操作相关文本
    constexpr std::string_view InfoQueryPrompt = "Info: Please enter an ID to query.";
    constexpr std::string_view ResultIDFoundPart1 = "Result: ID '";
    constexpr std::string_view ResultIDFoundPart2 = "' was found.";
    constexpr std::string_view ResultIDNotFoundPart1 = "Result: ID '";
    constexpr std::string_view ResultIDNotFoundPart2 = "' does not exist.";
}