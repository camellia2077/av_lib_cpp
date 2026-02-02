// adapters/input_parser.hpp
#ifndef INPUT_PARSER_HPP
#define INPUT_PARSER_HPP

#include <sstream>
#include <string>
#include <vector>

namespace Adapters {
inline std::vector<std::string> split_ids(const std::string &input) {
  std::istringstream iss(input);
  std::vector<std::string> ids;
  std::string token;
  while (iss >> token) {
    ids.push_back(token);
  }
  return ids;
}
} // namespace Adapters

#endif
