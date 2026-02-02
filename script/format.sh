#!/bin/bash

set -e

cd "$(dirname "$0")"

echo "--- 当前目录: $(pwd)"
echo "--- 运行 clang-format..."

ROOT_DIR="$(pwd)/.."

clang-format -i \
  $(find "$ROOT_DIR/src" -type f \( -name "*.cpp" -o -name "*.hpp" -o -name "*.h" \))
