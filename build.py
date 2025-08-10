import os
import sys
import subprocess
import pathlib
import platform
import shutil
import time  # 1. 导入 time 模块

# --- 配置 ---
BUILD_DIR = "build"

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
    # 2. 在所有操作开始前，记录开始时间
    start_time = time.monotonic()

    script_path = pathlib.Path(__file__).resolve().parent
    os.chdir(script_path)
    print(f"--- 已切换到工作目录: {os.getcwd()}")

    build_path = pathlib.Path(BUILD_DIR)
    build_path.mkdir(exist_ok=True)
    print(f"--- 构建目录 '{BUILD_DIR}' 已准备就绪 (不清空)。")
    
    # 配置CMake
    cmake_configure_command = ["cmake", "-S", ".", "-B", str(build_path)]
    cmake_configure_command.append("-D CMAKE_BUILD_TYPE=Release")
    # [新增] 添加参数以链接GLFW的动态库
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

    # 3. 在所有操作结束后，记录结束时间并计算差值
    end_time = time.monotonic()
    duration = end_time - start_time

    print("\n--- ✅ 构建成功！ ---")
    # 我们已经修改了CMakeLists.txt，所以这里的提示也更新一下
    print(f"--- 可执行文件位于 '{BUILD_DIR}/bin' 目录中。 ---") 
    print("--- 提示: 第一次编译会较慢，后续修改代码后的编译会因为缓存而加速。")
    # 4. 打印总耗时
    print(f"--- 总耗时: {duration:.2f} 秒 ---")


if __name__ == "__main__":
    main()