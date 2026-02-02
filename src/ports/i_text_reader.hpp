// ports/i_text_reader.hpp
#ifndef I_TEXT_READER_HPP
#define I_TEXT_READER_HPP

#include <stdexcept>
#include <string>
#include <vector>

class FileOpenException : public std::runtime_error {
public:
  explicit FileOpenException(const std::string &message)
      : std::runtime_error(message) {}
};

class ITextReader {
public:
  virtual ~ITextReader() = default;
  virtual std::vector<std::string>
  read_all_lines(const std::string &filepath) = 0;
};

#endif
