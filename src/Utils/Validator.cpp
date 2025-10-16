// Utils/Validator.cpp
#include "Validator.hpp"
#include <string>

// 字符类型判断函数已移至 Validator.hpp

bool Validator::isValidIDFormat(const std::string& id) {
    std::string alpha_part;
    std::string digit_part;

    // 使用状态机来解析输入字符串，新逻辑支持'-'作为分隔符
    enum class ParseState {
        READING_ALPHA,       // 正在读取字母部分
        READING_SEPARATOR,   // 正在读取分隔符 (空格或'-')
        READING_DIGITS       // 正在读取数字部分
    };

    ParseState current_state = ParseState::READING_ALPHA;
    bool hyphen_seen = false; // 标记是否已遇到'-'

    for (const char c : id) {
        switch (current_state) {
            case ParseState::READING_ALPHA:
                if (is_alpha_char(c)) {
                    alpha_part += c;
                } else if (is_digit_char(c)) {
                    // 字母部分结束，直接进入数字部分
                    if (alpha_part.empty()) return false; // ID不能以数字开头
                    current_state = ParseState::READING_DIGITS;
                    digit_part += c;
                } else if (is_space_char(c) || c == '-') {
                    // 字母部分结束，进入分隔符部分
                    if (alpha_part.empty()) return false; // ID不能以分隔符开头
                    current_state = ParseState::READING_SEPARATOR;
                    if (c == '-') {
                        hyphen_seen = true;
                    }
                } else {
                    return false; // 字母区段出现无效字符
                }
                break;

            case ParseState::READING_SEPARATOR:
                if (is_digit_char(c)) {
                    // 分隔符结束后，开始读取数字
                    current_state = ParseState::READING_DIGITS;
                    digit_part += c;
                } else if (c == '-') {
                    if (hyphen_seen) return false; // 不允许多个'-'
                    hyphen_seen = true;
                } else if (!is_space_char(c)) {
                    return false; // 分隔符区段出现无效字符 (如字母)
                }
                // 如果是空格，则继续忽略
                break;

            case ParseState::READING_DIGITS:
                if (is_digit_char(c)) {
                    digit_part += c;
                } else {
                    return false; // 数字区段出现无效字符 (如空格, '-', 或字母)
                }
                break;
        }
    }

    // --- 关键修改点 ---
    // 循环结束后，必须成功进入并完成数字读取阶段
    if (current_state != ParseState::READING_DIGITS || digit_part.empty()) {
        // 此检查会拒绝如 "abc-" 或 "abc " 这样以分隔符结尾的无效输入
        return false;
    }

    // 根据收集到的字母和数字部分的长度进行最终验证
    const size_t alpha_len = alpha_part.length();
    const size_t digit_len = digit_part.length();

    // 字母长度和数字长度
    bool is_alpha_len_valid = (alpha_len >= 1); // 字母部分至少为1个
    bool is_digit_len_valid = (digit_len >= 1);// 数字部分少为1个

    return is_alpha_len_valid && is_digit_len_valid;
}