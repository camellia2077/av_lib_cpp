// io/text_file_reader.hpp
#ifndef TEXT_FILE_READER_HPP
#define TEXT_FILE_READER_HPP

#include "ports/i_text_reader.hpp"
#include <string>
#include <vector>

namespace IO {
class TextFileReader : public ITextReader {
public:
  // 读取文件所有行，如果失败则抛出异常
  std::vector<std::string> read_all_lines(const std::string &filepath) override;
};
} // namespace IO

#endif // TEXT_FILE_READER_HPP
