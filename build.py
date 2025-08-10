import os
import sys
import subprocess
import pathlib
import platform

# --- 配置 ---
# CMAKE 构建目录的名称
BUILD_DIR = "build"

def run_command(command):
    """辅助函数：打印并执行一个命令，如果失败则退出程序"""
    print(f"--- Executing: {' '.join(command)}")
    try:
        # 使用 check=True，如果命令返回非零退出码（表示错误），会自动抛出异常
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
    # 1. 切换到脚本所在的目录
    # 这是确保所有相对路径（如"."和BUILD_DIR）都正确的关键步骤
    script_path = pathlib.Path(__file__).resolve().parent
    os.chdir(script_path)
    print(f"--- 已切换到工作目录: {os.getcwd()}")

    # 2. 创建构建目录（如果它不存在）
    build_path = pathlib.Path(BUILD_DIR)
    build_path.mkdir(exist_ok=True)
    print(f"--- 构建目录 '{BUILD_DIR}' 已准备就绪。")
    
    # 3. 配置CMake (cmake -S . -B build)
    #    -S .       指定源码根目录为当前目录
    #    -B build   指定构建目录
    cmake_configure_command = ["cmake", "-S", ".", "-B", str(build_path)]
    
    # 可选：为不同平台添加特定的生成器 (Generator)
    # 在Windows上，使用Visual Studio通常更好
    if platform.system() == "Windows":
        # 你可以根据你安装的Visual Studio版本进行修改
        # 例如 "Visual Studio 17 2022" 或 "Visual Studio 16 2019"
        # 如果不指定，CMake会尝试找到一个可用的
        pass # 留空让CMake自动检测
    # 在Linux或macOS上，"Unix Makefiles" 是默认的，通常无需指定
    elif platform.system() == "Linux" or platform.system() == "Darwin":
        cmake_configure_command.extend(["-G", "Unix Makefiles"])

    run_command(cmake_configure_command)

    # 4. 执行编译 (cmake --build build)
    #    --build  告诉cmake执行构建步骤
    #    --config Release  (可选)指定构建类型为Release，以获得优化
    cmake_build_command = ["cmake", "--build", str(build_path), "--config", "Release"]
    
    run_command(cmake_build_command)

    print("\n--- ✅ 构建成功！ ---")
    print(f"--- 可执行文件位于 '{BUILD_DIR}' 目录中。 ---")


if __name__ == "__main__":
    main()