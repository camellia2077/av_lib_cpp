cmake_minimum_required(VERSION 3.16)
project(FastQueryApp)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# -------------------------------------------------------------------
# --- ImGui 库定义 (无需改动) ---
add_library(imgui SHARED
    lib/imgui/imgui.cpp
    lib/imgui/imgui_draw.cpp
    lib/imgui/imgui_tables.cpp
    lib/imgui/imgui_widgets.cpp
    lib/imgui/backends/imgui_impl_glfw.cpp
    lib/imgui/backends/imgui_impl_opengl3.cpp
)
target_include_directories(imgui PUBLIC
    lib/imgui
    lib/imgui/backends
)
target_link_libraries(imgui PUBLIC
    glfw
    ${OPENGL_LIBRARIES}
)
# -------------------------------------------------------------------

# --- 查找依赖库 (无需改动) ---
find_package(glfw3 3.3 REQUIRED)
find_package(OpenGL REQUIRED)

# --- 自动发现源文件 (无需改动) ---
file(GLOB APP_SOURCES "src/App/*.cpp")
file(GLOB DATA_SOURCES "src/Data/*.cpp")
file(GLOB VIEW_SOURCES "src/View/ImGui/*.cpp")
file(GLOB UTILS_SOURCES "src/Utils/*.cpp")


# --- 定义可执行文件 ---

# 1. GUI 版本 (MyApp)
add_executable(MyApp WIN32
    src/main.cpp
    ${APP_SOURCES}
    ${DATA_SOURCES}
    ${VIEW_SOURCES}
    ${UTILS_SOURCES}
)

# 2. 命令行版本 (MyApp_Cmd)
# 注意：这里不包含 VIEW_SOURCES
add_executable(MyApp_Cmd
    src/cmd_main.cpp
    ${APP_SOURCES}
    ${DATA_SOURCES}
    ${UTILS_SOURCES}
)


# --- 为 MyApp (GUI版本) 配置 ---
target_include_directories(MyApp PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}/src/common
)
target_compile_options(MyApp PRIVATE
    -Os
    -march=native
)
target_precompile_headers(MyApp PRIVATE
    "src/common/pch.h"
)
target_link_libraries(MyApp PRIVATE
    imgui
    glfw
    "-s"
    ${OPENGL_LIBRARIES}
)

# --- 为 MyApp_Cmd (命令行版本) 配置 ---
target_include_directories(MyApp_Cmd PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}/src/common
)
# [修改点] 为命令行版本添加编译优化选项
target_compile_options(MyApp_Cmd PRIVATE
    -Os
    -march=native
)
# [修改点] 为命令行版本添加链接选项以减小体积
target_link_options(MyApp_Cmd PRIVATE "-s")

target_precompile_headers(MyApp_Cmd PRIVATE
    "src/common/cmd_pch.h"
)
# 注意：命令行版本不需要链接任何GUI库