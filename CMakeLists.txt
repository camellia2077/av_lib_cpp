cmake_minimum_required(VERSION 3.16)
project(FastQueryApp)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# 推荐保留：确保跨平台编码一致性
# add_compile_options(-finput-charset=UTF-8 -fexec-charset=UTF-8)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# -------------------------------------------------------------------
# --- 手动为 ImGui 创建库 (此部分无需改动) ---
add_library(imgui
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
# -------------------------------------------------------------------

# --- 查找依赖库: GLFW 和 OpenGL (此部分无需改动) ---
find_package(glfw3 3.3 REQUIRED)
find_package(OpenGL REQUIRED)

# --- 定义可执行文件 ---
# 最佳实践：只列出.cpp源文件，不列出.h文件，也不需要pch.cpp
add_executable(MyApp WIN32
    src/main.cpp
    # App 层
    src/App/Application.cpp
    # Data 层
    src/Data/FastQueryDB.cpp
    # View 层
    src/View/ImGuiView.cpp
    # Utils 层
    src/Utils/Validator.cpp
)

# --- [核心改动 1] 添加头文件搜索路径 ---
# 将根src目录和新的common目录都加入，以便#include能正确找到所有头文件
target_include_directories(MyApp PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_SOURCE_DIR}/src/common # <-- 新增此行
)

# --- [核心改动 2] 使用 target_precompile_headers 配置 PCH ---
# 直接将 pch.h 文件设置为预编译头。CMake 会自动处理生成和使用。
target_precompile_headers(MyApp PRIVATE
    "src/common/pch.h" # <-- CMake 会在 include directories 中查找它
)

# --- 链接所有需要的库 (此部分无需改动) ---
target_link_libraries(MyApp PRIVATE
    imgui               # ImGui 库本身
    glfw                # GLFW 窗口库
    ${OPENGL_LIBRARIES} # OpenGL
)