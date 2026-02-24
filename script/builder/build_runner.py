import os
import platform
import shutil
import time

from .cmake_utils import cmake_define, run_command
from .paths import SCRIPT_DIR, SOURCE_DIR


def get_mode_config(mode):
    if mode == "release":
        build_dir = SOURCE_DIR / "build"
        build_type = "Release"
        extra_defines = [cmake_define("AVLIB_STATIC_LINK", "ON")]
        build_target = None
    elif mode == "fast":
        build_dir = SOURCE_DIR / "build_fast"
        build_type = "Debug"
        extra_defines = [
            cmake_define("AVLIB_STATIC_LINK", "ON"),
            cmake_define("CMAKE_CXX_FLAGS_DEBUG", "-O0 -g0 -fno-lto"),
            cmake_define("CMAKE_INTERPROCEDURAL_OPTIMIZATION", "OFF"),
            cmake_define("CMAKE_EXE_LINKER_FLAGS_DEBUG", "-fno-lto"),
            cmake_define("CMAKE_SHARED_LINKER_FLAGS_DEBUG", "-fno-lto"),
        ]
        build_target = None
    elif mode == "tidy":
        build_dir = SOURCE_DIR / "build_tidy"
        build_type = "Debug"
        extra_defines = [
            cmake_define("AVLIB_STATIC_LINK", "ON"),
            cmake_define("ENABLE_CLANG_TIDY", "ON"),
            cmake_define("CMAKE_DISABLE_PRECOMPILE_HEADERS", "ON"),
            cmake_define("CLANG_TIDY_FIX", "ON"),
            cmake_define("CLANG_TIDY_HEADER_FILTER", ".*/src/.*"),
        ]
        build_target = "tidy"
    else:
        raise ValueError(f"未知构建模式: {mode}")

    return build_dir, build_type, extra_defines, build_target


def run_build(args):
    start_time = time.monotonic()

    os.chdir(SCRIPT_DIR)
    print(f"--- 已切换到工作目录: {os.getcwd()}")
    print(f"--- 构建模式: {args.mode}")

    build_path, build_type, extra_defines, build_target = get_mode_config(args.mode)
    build_path.mkdir(exist_ok=True)
    print(f"--- 构建目录 '{build_path}' 已准备就绪 (不清空)。")

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

    cmake_build_command = ["cmake", "--build", str(build_path), "--config", build_type]
    if build_target:
        cmake_build_command.extend(["--target", build_target])

    run_command(cmake_build_command)

    duration = time.monotonic() - start_time

    print("\n--- 构建完成 ---")
    if build_target:
        print(f"--- 目标 '{build_target}' 执行完成。")
    else:
        print(f"--- 可执行文件位于 '{build_path}/bin' 目录中。 ---")
    print("--- 提示: 第一次编译会较慢，后续修改代码后的编译会因为缓存而加速。")
    print(f"--- 总耗时: {duration:.2f} 秒 ---")

    return 0
