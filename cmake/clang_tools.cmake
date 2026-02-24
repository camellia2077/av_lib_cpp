option(ENABLE_CLANG_TIDY "Enable clang-tidy during build" OFF)
option(ENABLE_CLANG_FORMAT "Enable clang-format target" ON)
option(CLANG_TIDY_FIX "Apply clang-tidy fixes" OFF)
set(CLANG_TIDY_HEADER_FILTER "" CACHE STRING "Header filter regex for clang-tidy")

if(ENABLE_CLANG_TIDY)
    set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
    find_program(CLANG_TIDY_EXE clang-tidy)
    if(CLANG_TIDY_EXE)
        set(CMAKE_CXX_CLANG_TIDY "${CLANG_TIDY_EXE}")
        set(TIDY_SOURCES
            ${CORE_SOURCES}
            ${CLI_SOURCES}
            ${GUI_SOURCES}
            ${GUI_ENTRY_SOURCE}
            ${CMD_ENTRY_SOURCE}
        )
        find_package(Python3 COMPONENTS Interpreter)
        if(Python3_Interpreter_FOUND)
            set(_clang_tidy_runner "${CMAKE_CURRENT_SOURCE_DIR}/script/build.py")
            set(_clang_tidy_runner_args
                --run-clang-tidy
                --build-dir "${CMAKE_BINARY_DIR}"
                --clang-tidy "${CLANG_TIDY_EXE}"
            )
            if(CLANG_TIDY_FIX)
                list(APPEND _clang_tidy_runner_args --fix --format-style=file)
            endif()
            if(CLANG_TIDY_HEADER_FILTER)
                list(APPEND _clang_tidy_runner_args --header-filter "${CLANG_TIDY_HEADER_FILTER}")
            endif()
            if(DEFINED ENV{CMAKE_BUILD_PARALLEL_LEVEL} AND NOT "$ENV{CMAKE_BUILD_PARALLEL_LEVEL}" STREQUAL "")
                list(APPEND _clang_tidy_runner_args --jobs "$ENV{CMAKE_BUILD_PARALLEL_LEVEL}")
            endif()
            add_custom_target(tidy
                COMMAND "${Python3_EXECUTABLE}" -u "${_clang_tidy_runner}" ${_clang_tidy_runner_args} ${TIDY_SOURCES}
                WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                COMMENT "Running clang-tidy on source files (parallel)"
            )
        else()
            message(WARNING "Python3 not found; falling back to single-process clang-tidy target.")
            set(_clang_tidy_args "")
            if(CLANG_TIDY_FIX)
                list(APPEND _clang_tidy_args -fix -format-style=file)
            endif()
            if(CLANG_TIDY_HEADER_FILTER)
                list(APPEND _clang_tidy_args "-header-filter=${CLANG_TIDY_HEADER_FILTER}")
            endif()
            add_custom_target(tidy
                COMMAND ${CLANG_TIDY_EXE} -p ${CMAKE_BINARY_DIR} ${_clang_tidy_args} ${TIDY_SOURCES}
                WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
                COMMENT "Running clang-tidy on source files"
            )
        endif()
    else()
        message(WARNING "clang-tidy not found; ENABLE_CLANG_TIDY ignored.")
    endif()
endif()

if(ENABLE_CLANG_FORMAT)
    find_program(CLANG_FORMAT_EXE clang-format)
    if(CLANG_FORMAT_EXE)
        file(GLOB_RECURSE CLANG_FORMAT_SOURCES CONFIGURE_DEPENDS
            "${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/*.hpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/*.h"
        )
        add_custom_target(format
            COMMAND ${CLANG_FORMAT_EXE} -i ${CLANG_FORMAT_SOURCES}
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
            COMMENT "Running clang-format on source files"
        )
    else()
        message(WARNING "clang-format not found; format target not created.")
    endif()
endif()
