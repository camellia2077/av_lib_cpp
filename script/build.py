import os
import sys
import subprocess
import pathlib
import platform
import shutil
import time

# --- 配置 ---
# [修改] 定义了项目的根目录 (CMakeLists.txt 所在位置)
SOURCE_DIR = r"C:\Computer\my_github\github_cpp\av_lib\av_lib_cpp" 
BUILD_DIR = r"C:\Computer\my_github\github_cpp\av_lib\av_lib_cpp\build"

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

def main():
    """主构建函数"""
    start_time = time.monotonic()

    # 这部分代码可以保留，对于某些脚本操作可能仍然有用
    script_path = pathlib.Path(__file__).resolve().parent
    os.chdir(script_path)
    print(f"--- 已切换到工作目录: {os.getcwd()}")

    build_path = pathlib.Path(BUILD_DIR)
    build_path.mkdir(exist_ok=True)
    print(f"--- 构建目录 '{BUILD_DIR}' 已准备就绪 (不清空)。")
    
    # 配置CMake
    # [修改] 使用 SOURCE_DIR 变量作为 CMake 的源目录
    cmake_configure_command = ["cmake", "-S", SOURCE_DIR, "-B", str(build_path)]
    cmake_configure_command.append("-D CMAKE_BUILD_TYPE=Release")
    cmake_configure_command.append("-Dglfw3_SHARED_LIBS=ON")
    
    if shutil.which("ccache"):
        print("--- 检测到 ccache，自动启用。")
        cmake_configure_command.append("-D CMAKE_CXX_COMPILER_LAUNCHER=ccache")
    else:
        print("--- 未检测到 ccache，将使用默认编译器。")

    if platform.system() == "Linux" or platform.system() == "Darwin":
        cmake_configure_command.extend(["-G", "Unix Makefiles"])

    run_command(cmake_configure_command)

    # 执行编译
    cmake_build_command = ["cmake", "--build", str(build_path), "--config", "Release"]
    
    run_command(cmake_build_command)

    end_time = time.monotonic()
    duration = end_time - start_time

    print("\n--- ✅ 构建成功！ ---")
    print(f"--- 可执行文件位于 '{BUILD_DIR}/bin' 目录中。 ---") 
    print("--- 提示: 第一次编译会较慢，后续修改代码后的编译会因为缓存而加速。")
    print(f"--- 总耗时: {duration:.2f} 秒 ---")


if __name__ == "__main__":
    main()