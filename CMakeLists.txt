cmake_minimum_required(VERSION 3.16)
project(FastQueryApp)

# 新增下面这行，告诉编译器源文件和执行文件都使用UTF-8
# add_compile_options(-finput-charset=UTF-8 -fexec-charset=UTF-8)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# -------------------------------------------------------------------
# --- 手动为 ImGui 创建库 ---
# 因为官方 ImGui 不带 CMakeLists.txt，我们直接告诉 CMake 要编译哪些文件
# 这是处理这类库的标准方法。
add_library(imgui
    # ImGui 核心文件
    lib/imgui/imgui.cpp
    lib/imgui/imgui_draw.cpp
    lib/imgui/imgui_tables.cpp
    lib/imgui/imgui_widgets.cpp
    # ImGui 后端文件 (我们的项目需要它们)
    lib/imgui/backends/imgui_impl_glfw.cpp
    lib/imgui/backends/imgui_impl_opengl3.cpp
)

# 告诉其他目标，在使用 imgui 库时，需要包含哪些头文件目录
target_include_directories(imgui PUBLIC
    lib/imgui
    lib/imgui/backends
)
# -------------------------------------------------------------------

# --- 查找依赖库: GLFW 和 OpenGL ---
find_package(glfw3 3.3 REQUIRED)
find_package(OpenGL REQUIRED)

# --- 定义可执行文件 ---
add_executable(MyApp WIN32
    src/main.cpp
    # App 层
    src/App/Application.cpp
    src/App/Application.h
    # Data 层
    src/Data/FastQueryDB.cpp
    src/Data/FastQueryDB.h
    # View 层
    src/View/ImGuiView.cpp
    src/View/ImGuiView.h
    src/View/IGuiView.h
)

# --- 链接所有需要的库 ---
# 这里的代码无需改动，它现在会链接到我们上面手动创建的 imgui 库
target_link_libraries(MyApp PRIVATE
    imgui               # ImGui 库本身
    glfw                # GLFW 窗口库
    ${OPENGL_LIBRARIES} # OpenGL
)

# 包含头文件目录
target_include_directories(MyApp PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)