// io/text_file_reader.hpp
#ifndef TEXT_FILE_READER_HPP
#define TEXT_FILE_READER_HPP

#include <string>
#include <vector>

#include "ports/i_text_reader.hpp"

namespace IO {
class TextFileReader : public ITextReader {
 public:
  // 读取文件所有行，如果失败则抛出异常
  auto ReadAllLines(const std::string& filepath)
      -> std::vector<std::string> override;
};
}  // namespace IO

#endif  // TEXT_FILE_READER_HPP
