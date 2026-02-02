import argparse
import os
import sys
import subprocess
import pathlib
import platform
import shutil
import time

# --- 配置 ---
SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
SOURCE_DIR = SCRIPT_DIR.parent

def run_command(command):
    """辅助函数：打印并执行一个命令，如果失败则退出程序"""
    print(f"--- Executing: {' '.join(command)}")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"--- !!! 命令执行失败，返回码: {e.returncode}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"--- !!! 错误: 命令 '{command[0]}' 未找到。", file=sys.stderr)
        print("--- 请确保 cmake 或你的编译工具已安装并位于系统的PATH中。", file=sys.stderr)
        sys.exit(1)

def cmake_define(name, value):
    return f"-D{name}={value}"

def parse_args():
    parser = argparse.ArgumentParser(description="项目构建入口")
    parser.add_argument(
        "--mode",
        choices=["release", "fast", "tidy"],
        default="release",
        help="构建模式: release|fast|tidy",
    )
    return parser.parse_args()

def get_mode_config(mode):
    if mode == "release":
        build_dir = SOURCE_DIR / "build"
        build_type = "Release"
        extra_defines = [cmake_define("glfw3_SHARED_LIBS", "ON")]
        build_target = None
    elif mode == "fast":
        build_dir = SOURCE_DIR / "build_fast"
        build_type = "Debug"
        extra_defines = [
            cmake_define("CMAKE_CXX_FLAGS_DEBUG", "-O0 -g0 -fno-lto"),
            cmake_define("CMAKE_INTERPROCEDURAL_OPTIMIZATION", "OFF"),
            cmake_define("CMAKE_EXE_LINKER_FLAGS_DEBUG", "-fno-lto"),
            cmake_define("CMAKE_SHARED_LINKER_FLAGS_DEBUG", "-fno-lto"),
        ]
        build_target = None
    elif mode == "tidy":
        build_dir = SOURCE_DIR / "build_debug"
        build_type = "Debug"
        extra_defines = [
            cmake_define("ENABLE_CLANG_TIDY", "ON"),
            cmake_define("CMAKE_DISABLE_PRECOMPILE_HEADERS", "ON"),
            cmake_define("CLANG_TIDY_FIX", "ON"),
            cmake_define("CLANG_TIDY_HEADER_FILTER", ".*/src/.*"),
        ]
        build_target = "tidy"
    else:
        raise ValueError(f"未知构建模式: {mode}")

    return build_dir, build_type, extra_defines, build_target

def main():
    """主构建函数"""
    args = parse_args()
    start_time = time.monotonic()

    os.chdir(SCRIPT_DIR)
    print(f"--- 已切换到工作目录: {os.getcwd()}")
    print(f"--- 构建模式: {args.mode}")

    build_path, build_type, extra_defines, build_target = get_mode_config(args.mode)
    build_path.mkdir(exist_ok=True)
    print(f"--- 构建目录 '{build_path}' 已准备就绪 (不清空)。")

    # 配置CMake
    cmake_configure_command = [
        "cmake",
        "-S",
        str(SOURCE_DIR),
        "-B",
        str(build_path),
        cmake_define("CMAKE_BUILD_TYPE", build_type),
    ]
    cmake_configure_command.extend(extra_defines)

    if shutil.which("ccache"):
        print("--- 检测到 ccache，自动启用。")
        cmake_configure_command.append(cmake_define("CMAKE_CXX_COMPILER_LAUNCHER", "ccache"))
    else:
        print("--- 未检测到 ccache，将使用默认编译器。")

    if platform.system() in ("Linux", "Darwin"):
        cmake_configure_command.extend(["-G", "Unix Makefiles"])

    run_command(cmake_configure_command)

    # 执行编译
    cmake_build_command = ["cmake", "--build", str(build_path), "--config", build_type]
    if build_target:
        cmake_build_command.extend(["--target", build_target])

    run_command(cmake_build_command)

    end_time = time.monotonic()
    duration = end_time - start_time

    print("\n--- 构建完成 ---")
    if build_target:
        print(f"--- 目标 '{build_target}' 执行完成。")
    else:
        print(f"--- 可执行文件位于 '{build_path}/bin' 目录中。 ---")
    print("--- 提示: 第一次编译会较慢，后续修改代码后的编译会因为缓存而加速。")
    print(f"--- 总耗时: {duration:.2f} 秒 ---")


if __name__ == "__main__":
    main()
