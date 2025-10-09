cmake_minimum_required(VERSION 3.16)
project(FastQueryApp)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# --- [新增] 使用变量定义可执行文件名 ---
set(GUI_EXECUTABLE_NAME "MyAVLib_Gui")
set(CMD_EXECUTABLE_NAME "MyAVLib_Cmd")

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

# --- 查找依赖库 ---
find_package(glfw3 3.3 REQUIRED)
find_package(OpenGL REQUIRED)
find_package(SQLite3 REQUIRED)


# --- 自动发现源文件 ---
file(GLOB APP_SOURCES "src/App/*.cpp")
file(GLOB DATA_SOURCES 
    "src/Data/*.cpp"
)
file(GLOB VIEW_SOURCES "src/View/ImGui/*.cpp")
file(GLOB UTILS_SOURCES "src/Utils/*.cpp")
file(GLOB COMMON_SOURCES "src/common/*.cpp") 


# --- 定义可执行文件 ---

# 1. GUI 版本
add_executable(${GUI_EXECUTABLE_NAME} WIN32
    src/main.cpp
    ${APP_SOURCES}
    ${DATA_SOURCES}
    ${VIEW_SOURCES}
    ${UTILS_SOURCES}
    ${COMMON_SOURCES}
)

# 2. 命令行版本
add_executable(${CMD_EXECUTABLE_NAME}
    src/cmd_main.cpp
    ${APP_SOURCES}
    ${DATA_SOURCES}
    ${UTILS_SOURCES}
    ${COMMON_SOURCES}
)


# --- 为 GUI版本 配置 ---
target_include_directories(${GUI_EXECUTABLE_NAME} PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}/src/common
)
target_compile_options(${GUI_EXECUTABLE_NAME} PRIVATE
    -Os
    -march=native
)
target_precompile_headers(${GUI_EXECUTABLE_NAME} PRIVATE
    "src/common/pch.h"
)
target_link_libraries(${GUI_EXECUTABLE_NAME} PRIVATE
    imgui
    glfw
    "-s"
    ${OPENGL_LIBRARIES}
    SQLite::SQLite3
)

# --- 为 命令行版本 配置 ---
target_include_directories(${CMD_EXECUTABLE_NAME} PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}/src/common
)
target_compile_options(${CMD_EXECUTABLE_NAME} PRIVATE
    -Os
    -march=native
)
target_link_options(${CMD_EXECUTABLE_NAME} PRIVATE "-s")
target_precompile_headers(${CMD_EXECUTABLE_NAME} PRIVATE
    "src/common/cmd_pch.h"
)
target_link_libraries(${CMD_EXECUTABLE_NAME} PRIVATE
    SQLite::SQLite3
)