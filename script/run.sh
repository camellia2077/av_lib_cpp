#!/bin/bash

# set -e: 确保脚本中的任何命令失败时，脚本会立即退出。
set -e

# 切换到脚本所在的目录
# "$0" 是脚本本身的名称
# dirname "$0" 是脚本所在的目录
# cd "$(dirname "$0")" 能保证无论你从哪个路径下调用此脚本，
# 它总能先切换到自己的目录下再执行后续命令。
cd "$(dirname "$0")"

# 打印当前工作目录进行确认
echo "--- 当前目录: $(pwd)"

# 执行Python构建脚本
# 在msys2 环境中，建议使用 python3 而不是 py
echo "--- 启动Python构建脚本..."
python3 build.py