// IO/TextFileReader.hpp
#ifndef TEXT_FILE_READER_HPP
#define TEXT_FILE_READER_HPP

#include <string>
#include <vector>
#include <stdexcept>

// 自定义异常，让错误类型更明确
// 打开一个文本文件，将它的内容逐行读入一个字符串向量中
class FileOpenException : public std::runtime_error {
public:
    explicit FileOpenException(const std::string& message) 
        : std::runtime_error(message) {}
};

namespace IO {
    class TextFileReader {
    public:
        // 读取文件所有行，如果失败则抛出异常
        static std::vector<std::string> read_all_lines(const std::string& filepath);
    };
}

#endif // TEXT_FILE_READER_HPP