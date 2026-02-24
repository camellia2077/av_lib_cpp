#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BUILD_DIR="${BUILD_DIR:-${SOURCE_DIR}/build_tidy}"

cmake_args=(
  -S "${SOURCE_DIR}"
  -B "${BUILD_DIR}"
  -D CMAKE_BUILD_TYPE=Debug
  -D ENABLE_CLANG_TIDY=ON
  -D CLANG_TIDY_FIX=OFF
  -D CLANG_TIDY_HEADER_FILTER=".*/src/.*"
  -D CMAKE_DISABLE_PRECOMPILE_HEADERS=ON
)

if command -v ccache >/dev/null 2>&1; then
  cmake_args+=(-D CMAKE_CXX_COMPILER_LAUNCHER=ccache)
fi

cmake "${cmake_args[@]}"

if [[ -z "${CMAKE_BUILD_PARALLEL_LEVEL:-}" ]]; then
  if command -v nproc >/dev/null 2>&1; then
    export CMAKE_BUILD_PARALLEL_LEVEL="$(nproc)"
  elif command -v getconf >/dev/null 2>&1; then
    export CMAKE_BUILD_PARALLEL_LEVEL="$(getconf _NPROCESSORS_ONLN)"
  fi
fi

cmake --build "${BUILD_DIR}" --config Debug --target tidy
