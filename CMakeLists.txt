cmake_minimum_required(VERSION 3.16)
project(FastQueryApp)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# 推荐保留：确保跨平台编码一致性
# add_compile_options(-finput-charset=UTF-8 -fexec-charset=UTF-8)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# -------------------------------------------------------------------
# --- 手动为 ImGui 创建库 (此部分无需改动) ---
add_library(imgui SHARED
    lib/imgui/imgui.cpp
    lib/imgui/imgui_draw.cpp
    lib/imgui/imgui_tables.cpp
    lib/imgui/imgui_widgets.cpp
    lib/imgui/backends/imgui_impl_glfw.cpp
    lib/imgui/backends/imgui_impl_opengl3.cpp
)

# [新增] 为 imgui 库添加它自己的头文件搜索路径
target_include_directories(imgui PUBLIC
    lib/imgui
    lib/imgui/backends
)
# [新增] 为 imgui 库链接它所依赖的库
target_link_libraries(imgui PUBLIC
    glfw
    ${OPENGL_LIBRARIES}
)
# -------------------------------------------------------------------

# --- 查找依赖库: GLFW 和 OpenGL (此部分无需改动) ---
find_package(glfw3 3.3 REQUIRED)
find_package(OpenGL REQUIRED)

# --- [核心修改] 使用 file(GLOB ...) 自动发现源文件 ---
# 为每个逻辑目录（层）创建一个源文件列表变量
file(GLOB APP_SOURCES "src/App/*.cpp")
file(GLOB DATA_SOURCES "src/Data/*.cpp")
file(GLOB VIEW_SOURCES "src/View/ImGui/*.cpp")
file(GLOB UTILS_SOURCES "src/Utils/*.cpp")


# --- 定义可执行文件 ---
# 将所有源文件列表和 main.cpp 一起加入
add_executable(MyApp WIN32
    src/main.cpp
    ${APP_SOURCES}
    ${DATA_SOURCES}
    ${VIEW_SOURCES}
    ${UTILS_SOURCES}
)

# --- 添加头文件搜索路径 (保持不变) ---
# 将根src目录和新的common目录都加入，以便#include能正确找到所有头文件
target_include_directories(MyApp PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}/src/common
)

# --- [新增] 为 MyApp 添加特定的编译选项 ---
target_compile_options(MyApp PRIVATE
    -Os
    -march=native
)

# --- 使用 target_precompile_headers 配置 PCH (保持不变) ---
# 直接将 pch.h 文件设置为预编译头。CMake 会自动处理生成和使用。
target_precompile_headers(MyApp PRIVATE
    "src/common/pch.h"
)

# --- 链接所有需要的库 (保持不变) ---
target_link_libraries(MyApp PRIVATE
    imgui               # ImGui 库本身
    glfw                # GLFW 窗口库
    "-s"
    ${OPENGL_LIBRARIES} # OpenGL
)