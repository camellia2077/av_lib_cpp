if(AVLIB_STATIC_LINK)
    set(BUILD_SHARED_LIBS OFF)
    set(SQLite3_USE_STATIC_LIBS ON)
    set(CMAKE_FIND_LIBRARY_SUFFIXES ".a" ".lib")
    set(_imgui_lib_type STATIC)

    find_path(GLFW3_INCLUDE_DIR NAMES GLFW/glfw3.h REQUIRED)
    if(MINGW)
        find_file(GLFW3_STATIC_LIBRARY NAMES libglfw3.a PATH_SUFFIXES lib REQUIRED)
        set(GLFW3_LIBRARY "${GLFW3_STATIC_LIBRARY}")
    else()
        find_library(GLFW3_LIBRARY NAMES glfw3 REQUIRED)
    endif()

    add_library(glfw STATIC IMPORTED GLOBAL)
    set_target_properties(glfw PROPERTIES
        IMPORTED_LOCATION "${GLFW3_LIBRARY}"
        INTERFACE_INCLUDE_DIRECTORIES "${GLFW3_INCLUDE_DIR}"
    )
    if(WIN32)
        set_property(TARGET glfw APPEND PROPERTY
            INTERFACE_LINK_LIBRARIES gdi32
        )
    endif()
else()
    set(_imgui_lib_type SHARED)
    find_package(glfw3 3.3 REQUIRED)
endif()

find_package(OpenGL REQUIRED)
find_package(SQLite3 REQUIRED)

add_library(imgui ${_imgui_lib_type}
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/imgui/imgui.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/imgui/imgui_draw.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/imgui/imgui_tables.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/imgui/imgui_widgets.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/imgui/backends/imgui_impl_glfw.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/imgui/backends/imgui_impl_opengl3.cpp
)
target_include_directories(imgui PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/imgui
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/imgui/backends
)
target_link_libraries(imgui PUBLIC
    glfw
    ${OPENGL_LIBRARIES}
)
