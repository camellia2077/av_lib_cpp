set(GUI_ENTRY_SOURCE
    ${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp
)

set(CMD_ENTRY_SOURCE
    ${CMAKE_CURRENT_SOURCE_DIR}/src/cmd_main.cpp
)

set(CORE_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/app/application.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/data/fast_query_db.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/infrastructure/database_manager.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/io/text_file_reader.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/utils/validator.cpp
)

set(CLI_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/adapters/cli/framework/cli_app.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/adapters/cli/impl/CLICommands.cpp
)

set(GUI_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/view/imgui/framework/gui_app.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/view/imgui/impl/imgui_settings_store.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/view/imgui/impl/im_gui_view.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/view/imgui/impl/theme_manager.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/view/imgui/impl/ui_panel.cpp
)
