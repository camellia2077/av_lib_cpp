import subprocess
import sys


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
