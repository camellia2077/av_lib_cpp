// common/MessageFormatter.hpp
#ifndef MESSAGEFORMATTER_HPP
#define MESSAGEFORMATTER_HPP

#include "App/Application.hpp"
#include <string>

namespace MessageFormatter {

/**
 * @brief 根据应用状态和操作结果生成用户可读的消息字符串
 * * @param status 当前的应用状态枚举
 * @param result 上一次操作的结果
 * @param app 应用对象的引用，用于获取上下文信息 (如当前数据库名)
 * @return 格式化好的消息字符串
 */
std::string format_message(const Application& app);

} // namespace MessageFormatter
#endif