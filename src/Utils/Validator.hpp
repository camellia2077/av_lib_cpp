// utils/validator.hpp
#ifndef VALIDATOR_HPP
#define VALIDATOR_HPP

#include <string>

namespace Validator {
/**
 * @brief 验证ID格式是否正确
 * 规则: 2, 3或4个字母 (不区分大小写), 后跟2, 3或4位数字,
 * 中间可有空格或一个'-'作为分隔符。
 * @param id 要验证的ID字符串
 * @return 如果格式正确则返回true, 否则返回false
 */
auto IsValidIdFormat(const std::string& id) -> bool;

// --- 移至头文件的公共辅助函数 ---
// 使其在 Application.cpp 中也可用
inline auto IsAlphaChar(char c) -> bool {
  return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');
}

inline auto IsDigitChar(char c) -> bool {
  return c >= '0' && c <= '9';
}

inline auto IsSpaceChar(char c) -> bool {
  return c == ' ' || c == '\t';
}
}  // namespace Validator
#endif