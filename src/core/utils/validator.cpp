// core/utils/validator.cpp
#include "core/utils/validator.hpp"

#include <string>

auto Validator::IsValidIdFormat(const std::string& id) -> bool {
  std::string alpha_part;
  std::string digit_part;

  // 使用状态机来解析输入字符串，新逻辑支持'-'作为分隔符
  enum class ParseState {
    kReadingAlpha,      // 正在读取字母部分
    kReadingSeparator,  // 正在读取分隔符 (空格或'-')
    kReadingDigits      // 正在读取数字部分
  };

  ParseState current_state = ParseState::kReadingAlpha;
  bool hyphen_seen = false;  // 标记是否已遇到'-'

  for (const char kC : id) {
    switch (current_state) {
      case ParseState::kReadingAlpha:
        if (IsAlphaChar(kC)) {
          alpha_part += kC;
        } else if (IsDigitChar(kC)) {
          // 字母部分结束，直接进入数字部分
          if (alpha_part.empty()) {
            return false;  // ID不能以数字开头
          }
          current_state = ParseState::kReadingDigits;
          digit_part += kC;
        } else if (IsSpaceChar(kC) || kC == '-') {
          // 字母部分结束，进入分隔符部分
          if (alpha_part.empty()) {
            return false;  // ID不能以分隔符开头
          }
          current_state = ParseState::kReadingSeparator;
          if (kC == '-') {
            hyphen_seen = true;
          }
        } else {
          return false;  // 字母区段出现无效字符
        }
        break;

      case ParseState::kReadingSeparator:
        if (IsDigitChar(kC)) {
          // 分隔符结束后，开始读取数字
          current_state = ParseState::kReadingDigits;
          digit_part += kC;
        } else if (kC == '-') {
          if (hyphen_seen) {
            return false;  // 不允许多个'-'
          }
          hyphen_seen = true;
        } else if (!IsSpaceChar(kC)) {
          return false;  // 分隔符区段出现无效字符 (如字母)
        }
        // 如果是空格，则继续忽略
        break;

      case ParseState::kReadingDigits:
        if (IsDigitChar(kC)) {
          digit_part += kC;
        } else {
          return false;  // 数字区段出现无效字符 (如空格, '-', 或字母)
        }
        break;
    }
  }

  // --- 关键修改点 ---
  // 循环结束后，必须成功进入并完成数字读取阶段
  if (current_state != ParseState::kReadingDigits || digit_part.empty()) {
    // 此检查会拒绝如 "abc-" 或 "abc " 这样以分隔符结尾的无效输入
    return false;
  }

  // 根据收集到的字母 and 数字部分的长度进行最终验证
  const size_t kAlphaLen = alpha_part.length();
  const size_t kDigitLen = digit_part.length();

  // 字母长度 and 数字长度
  bool is_alpha_len_valid = (kAlphaLen >= 1);  // 字母部分至少为1个
  bool is_digit_len_valid = (kDigitLen >= 1);  // 数字部分至少为1个

  return is_alpha_len_valid && is_digit_len_valid;
}