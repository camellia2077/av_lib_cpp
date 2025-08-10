#include "common/pch.h"
#include "Validator.h"
#include <regex>

bool Validator::isValidIDFormat(const std::string& id) {
    // 正则表达式解释:
    // ^            - 字符串开始
    // [a-zA-Z]{3,4} - 匹配3到4个字母 (a-z, A-Z)
    // [0-9]{3,4}    - 匹配3到4个数字 (0-9)
    // $            - 字符串结束
    static const std::regex id_regex("^[a-zA-Z]{3,4}[0-9]{3,4}$");

    return std::regex_match(id, id_regex);
}