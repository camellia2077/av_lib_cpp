#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include "core/io/text_file_reader.hpp"
#include "core/utils/validator.hpp"

namespace {

auto Check(bool condition, const std::string& message) -> bool {
  if (!condition) {
    std::cerr << "FAILED: " << message << '\n';
    return false;
  }
  return true;
}

auto TestValidator() -> bool {
  bool ok = true;
  ok &= Check(Validator::IsValidIdFormat("abc-1234"), "validator accepts abc-1234");
  ok &= Check(Validator::IsValidIdFormat("A 1"), "validator accepts A 1");
  ok &= Check(Validator::IsValidIdFormat("ab12"), "validator accepts ab12");
  ok &= Check(!Validator::IsValidIdFormat("-ab12"), "validator rejects leading hyphen");
  ok &= Check(!Validator::IsValidIdFormat("ab-"), "validator rejects trailing separator");
  ok &= Check(!Validator::IsValidIdFormat("ab--12"), "validator rejects double hyphen");
  ok &= Check(!Validator::IsValidIdFormat("12ab"), "validator rejects leading digits");
  return ok;
}

auto TestTextFileReader() -> bool {
  IO::TextFileReader reader;
  const auto temp_file =
      std::filesystem::temp_directory_path() / "avlib_core_tests_input.txt";

  {
    std::ofstream out(temp_file.string(), std::ios::binary);
    out << "line1\r\nline2\nline3\r\n";
  }

  bool ok = true;
  try {
    const std::vector<std::string> lines = reader.ReadAllLines(temp_file.string());
    ok &= Check(lines.size() == 3, "text reader returns 3 lines");
    ok &= Check(lines[0] == "line1", "text reader keeps line1");
    ok &= Check(lines[1] == "line2", "text reader keeps line2");
    ok &= Check(lines[2] == "line3", "text reader trims CR");
  } catch (const std::exception& ex) {
    ok &= Check(false, std::string("text reader unexpected exception: ") + ex.what());
  }

  std::error_code ec;
  std::filesystem::remove(temp_file, ec);
  return ok;
}

}  // namespace

auto main() -> int {
  const bool validator_ok = TestValidator();
  const bool reader_ok = TestTextFileReader();
  if (validator_ok && reader_ok) {
    std::cout << "All core tests passed.\n";
    return 0;
  }
  return 1;
}
