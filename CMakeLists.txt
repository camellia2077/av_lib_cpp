cmake_minimum_required(VERSION 3.16)
project(FastQueryApp)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(FONTS_DIR ${CMAKE_CURRENT_SOURCE_DIR}/fonts)
option(AVLIB_STATIC_LINK "Prefer static linking to reduce runtime DLL dependencies" ON)

# --- 使用变量定义可执行文件名 ---
set(GUI_EXECUTABLE_NAME "MyAVLib_Gui")
set(CMD_EXECUTABLE_NAME "MyAVLib_Cmd")

# --- CMake 分层配置 ---
include(cmake/third_party.cmake)
include(cmake/sources.cmake)
include(cmake/clang_tools.cmake)


# --- 定义可执行文件 ---

# 1. GUI 版本
add_executable(${GUI_EXECUTABLE_NAME} WIN32
    ${GUI_ENTRY_SOURCE}
    ${CORE_SOURCES}
    ${GUI_SOURCES}
)

# 2. 命令行版本
add_executable(${CMD_EXECUTABLE_NAME}
    ${CMD_ENTRY_SOURCE}
    ${CORE_SOURCES}
    ${CLI_SOURCES}
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
    "src/common/pch.hpp"
)
target_link_libraries(${GUI_EXECUTABLE_NAME} PRIVATE
    imgui
    glfw
    "-s"
    ${OPENGL_LIBRARIES}
    SQLite::SQLite3
)
if(AVLIB_STATIC_LINK)
    if(MSVC)
        set_property(TARGET ${GUI_EXECUTABLE_NAME} PROPERTY
            MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
    elseif(MINGW)
        target_link_options(${GUI_EXECUTABLE_NAME} PRIVATE
            -static
            -static-libgcc
            -static-libstdc++
        )
    endif()
endif()

# --- 运行前复制字体资源 ---
add_custom_command(TARGET ${GUI_EXECUTABLE_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_directory
    ${FONTS_DIR}
    $<TARGET_FILE_DIR:${GUI_EXECUTABLE_NAME}>/fonts
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
    "src/common/cmd_pch.hpp"
)
target_link_libraries(${CMD_EXECUTABLE_NAME} PRIVATE
    SQLite::SQLite3
)
if(AVLIB_STATIC_LINK)
    if(MSVC)
        set_property(TARGET ${CMD_EXECUTABLE_NAME} PROPERTY
            MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>")
    elseif(MINGW)
        target_link_options(${CMD_EXECUTABLE_NAME} PRIVATE
            -static
            -static-libgcc
            -static-libstdc++
        )
    endif()
endif()
