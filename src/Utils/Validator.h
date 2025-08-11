#pragma once

#include <string>

namespace Validator {
    /**
     * @brief 验证ID格式是否正确
     * 规则: 2, 3或4个字母 (不区分大小写), 后跟2, 3或4位数字, 中间可有空格
     * @param id 要验证的ID字符串
     * @return 如果格式正确则返回true, 否则返回false
     */
    bool isValidIDFormat(const std::string& id);
}