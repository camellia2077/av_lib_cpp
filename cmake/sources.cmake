set(GUI_ENTRY_SOURCE
    ${CMAKE_CURRENT_SOURCE_DIR}/apps/gui/main.cpp
)

set(CMD_ENTRY_SOURCE
    ${CMAKE_CURRENT_SOURCE_DIR}/apps/cli/cmd_main.cpp
)

set(CORE_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/core/app/application.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/core/data/fast_query_db.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/core/infrastructure/database_manager.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/core/io/text_file_reader.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/src/core/utils/validator.cpp
)

set(CLI_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/apps/cli/framework/cli_app.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/apps/cli/impl/CLICommands.cpp
)

set(GUI_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/apps/gui/imgui/framework/gui_app.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/apps/gui/imgui/impl/imgui_settings_store.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/apps/gui/imgui/impl/im_gui_view.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/apps/gui/imgui/impl/theme_manager.cpp
    ${CMAKE_CURRENT_SOURCE_DIR}/apps/gui/imgui/impl/ui_panel.cpp
)
