import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="项目构建入口")
    parser.add_argument(
        "--mode",
        choices=["release", "fast", "tidy"],
        default="release",
        help="构建模式: release|fast|tidy",
    )
    parser.add_argument(
        "--run-clang-tidy",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--build-dir", default="", help="CMake build directory")
    parser.add_argument("--clang-tidy", default="clang-tidy", help="clang-tidy executable")
    parser.add_argument("--header-filter", default="", help="Header filter regex")
    parser.add_argument("--fix", action="store_true", help="Apply clang-tidy fixes")
    parser.add_argument("--format-style", default="", help="Format style for fixes")
    parser.add_argument("--jobs", type=int, default=0, help="Parallel jobs for clang-tidy")
    parser.add_argument("--tasks-dir", default="", help="Directory to write per-file logs")
    parser.add_argument("--log-file", default="", help="Combined log file path")
    parser.add_argument("files", nargs="*", help="Source files to check")
    return parser.parse_args()
