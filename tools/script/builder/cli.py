import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="项目脚本入口")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="配置并编译项目")
    build_parser.add_argument(
        "--mode",
        choices=["release", "fast", "tidy"],
        default="release",
        help="构建模式: release|fast|tidy",
    )

    tidy_parser = subparsers.add_parser("clang-tidy", help="执行 clang-tidy")
    tidy_parser.add_argument("--build-dir", required=True, help="CMake build directory")
    tidy_parser.add_argument("--clang-tidy", default="clang-tidy", help="clang-tidy executable")
    tidy_parser.add_argument("--header-filter", default="", help="Header filter regex")
    tidy_parser.add_argument("--fix", action="store_true", help="Apply clang-tidy fixes")
    tidy_parser.add_argument("--format-style", default="", help="Format style for fixes")
    tidy_parser.add_argument("--jobs", type=int, default=0, help="Parallel jobs for clang-tidy")
    tidy_parser.add_argument("--tasks-dir", default="", help="Directory to write per-file logs")
    tidy_parser.add_argument("--log-file", default="", help="Combined log file path")
    tidy_parser.add_argument("files", nargs="*", help="Source files to check")

    smoke_parser = subparsers.add_parser("smoke-cli", help="运行 CLI 冒烟测试")
    smoke_parser.add_argument("--exe-path", default="out/bin/MyAVLib_Cmd.exe", help="CLI executable path")

    core_test_parser = subparsers.add_parser("test-core", help="构建并运行 C++ 核心测试")
    core_test_parser.add_argument("--build-dir", default="out/build/tests", help="CMake build directory")
    core_test_parser.add_argument(
        "--config",
        default="Debug",
        choices=["Debug", "Release", "RelWithDebInfo", "MinSizeRel"],
        help="CMake build type",
    )

    return parser.parse_args()
