
#include "Validator.h"
#include <string>

// 零依赖的字符类型判断函数
namespace {
    inline bool is_alpha_char(char c) {
        return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');
    }

    inline bool is_digit_char(char c) {
        return c >= '0' && c <= '9';
    }
    
    inline bool is_space_char(char c) {
        return c == ' ' || c == '\t';
    }
}

bool Validator::isValidIDFormat(const std::string& id) {
    std::string alpha_part;
    std::string digit_part;

    // 使用状态机来解析输入字符串
    enum class ParseState {
        READING_ALPHA,   // 正在读取字母部分
        READING_GAP,     // 正在读取字母和数字之间的可选空格
        READING_DIGITS   // 正在读取数字部分
    };

    ParseState current_state = ParseState::READING_ALPHA;

    for (const char c : id) {
        switch (current_state) {
            case ParseState::READING_ALPHA:
                if (is_alpha_char(c)) {
                    alpha_part += c;
                } else if (is_digit_char(c)) {
                    // 字母部分结束，直接进入数字部分
                    current_state = ParseState::READING_DIGITS;
                    digit_part += c;
                } else if (is_space_char(c)) {
                    // 字母部分结束，进入中间的空格部分
                    current_state = ParseState::READING_GAP;
                } else {
                    return false; // 字母区段出现无效字符
                }
                break;

            case ParseState::READING_GAP:
                if (is_digit_char(c)) {
                    // 空格结束后，开始读取数字
                    current_state = ParseState::READING_DIGITS;
                    digit_part += c;
                } else if (!is_space_char(c)) {
                    return false; // 空格区段出现无效字符
                }
                // 如果是空格，则继续忽略
                break;

            case ParseState::READING_DIGITS:
                if (is_digit_char(c)) {
                    digit_part += c;
                } else {
                    return false; // 数字区段出现无效字符 (如空格或字母)
                }
                break;
        }
    }

    // --- 关键修改点 ---
    // 循环结束后，根据收集到的字母和数字部分的长度进行最终验证
    const size_t alpha_len = alpha_part.length();
    const size_t digit_len = digit_part.length();

    bool is_alpha_len_valid = (alpha_len >= 2 && alpha_len <= 4);
    // 将数字部分的有效长度改为2, 3或4
    bool is_digit_len_valid = (digit_len >= 2 && digit_len <= 4);

    return is_alpha_len_valid && is_digit_len_valid;
}