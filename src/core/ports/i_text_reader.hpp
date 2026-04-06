// core/ports/i_text_reader.hpp
#ifndef I_TEXT_READER_HPP
#define I_TEXT_READER_HPP

#include <stdexcept>
#include <string>
#include <vector>

class FileOpenException : public std::runtime_error {
 public:
  explicit FileOpenException(const std::string& message)
      : std::runtime_error(message) {}
};

class ITextReader {
 public:
  virtual ~ITextReader() = default;
  virtual auto ReadAllLines(const std::string& filepath)
      -> std::vector<std::string> = 0;
};

#endif
