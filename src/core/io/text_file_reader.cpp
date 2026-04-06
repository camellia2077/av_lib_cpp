// core/io/text_file_reader.cpp
#include "core/io/text_file_reader.hpp"

#include <fstream>
#include <string>
#include <vector>

namespace IO {

auto TextFileReader::ReadAllLines(const std::string& filepath)
    -> std::vector<std::string> {
  std::ifstream file(filepath);
  if (!file.is_open()) {
    throw std::runtime_error("无法打开文件: " + filepath);
  }

  std::vector<std::string> lines;
  std::string line;
  while (std::getline(file, line)) {
    // 移除可能存在的\r
    if (!line.empty() && line.back() == '\r') {
      line.pop_back();
    }
    lines.push_back(line);
  }

  return lines;
}

}  // namespace IO
