cmake_minimum_required(VERSION 3.21...3.27 FATAL_ERROR)

project(warn HOMEPAGE_URL https://github.com/petersteneteg/warn VERSION 1.0.0 LANGUAGES CXX)

find_package(Python3 COMPONENTS Interpreter REQUIRED)

set(WARN_EXTRA_WARNINGS_FILE "" CACHE FILEPATH "Extra warning table files")
if(WARN_EXTRA_WARNINGS_FILE)
    set(EXTRA_WARNINGS --extra_warnings "${WARN_EXTRA_WARNINGS_FILE}")
else()
     set(EXTRA_WARNINGS "")
endif()

set(WARN_HEADER_FILE "" CACHE FILEPATH "Optional header file to include at start of each file")
if(WARN_HEADER_FILE)
    set(HEADER --header "${WARN_HEADER_FILE}")
else()
     set(HEADER "")
endif()

execute_process(
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/warn.py" 
        --output_dir "${CMAKE_CURRENT_BINARY_DIR}/include"
        ${EXTRA_WARNINGS}
        ${HEADER}
    RESULT_VARIABLE returnCode
    OUTPUT_VARIABLE out
    ERROR_VARIABLE err
)
if(NOT returnCode EQUAL "0")
    message(FATAL_ERROR "Problem generating file: ${err}")
endif()

add_library(warn INTERFACE)
add_library(warn::warn ALIAS warn)

file(GLOB_RECURSE ignore_files ${CMAKE_CURRENT_BINARY_DIR}/include/warn/ignore/*)
target_sources(
    warn
    PUBLIC
    FILE_SET HEADERS
    TYPE HEADERS
    BASE_DIRS 
        ${CMAKE_CURRENT_BINARY_DIR}/include
    FILES
        ${ignore_files}
        ${CMAKE_CURRENT_BINARY_DIR}/include/warn/pop
        ${CMAKE_CURRENT_BINARY_DIR}/include/warn/push
        ${CMAKE_CURRENT_BINARY_DIR}/include/warn/warnings.md
)

option(WARN_INSTALL "Install warn" ON)
if(WARN_INSTALL)
    include(GNUInstallDirs)
    include(CMakePackageConfigHelpers)

    install(TARGETS warn EXPORT warnTargets 
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        FILE_SET HEADERS DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    )

    export(
        EXPORT warnTargets
        NAMESPACE warn::
        FILE ${PROJECT_BINARY_DIR}/warnConfig.cmake
    )

    install(
        EXPORT warnTargets 
        FILE warnConfig.cmake
        NAMESPACE warn:: 
        DESTINATION ${CMAKE_INSTALL_DATADIR}/warn
    )

    write_basic_package_version_file(
        ${CMAKE_CURRENT_BINARY_DIR}/warnConfigVersion.cmake
        COMPATIBILITY AnyNewerVersion
    )

    install(
        FILES ${CMAKE_CURRENT_BINARY_DIR}/warnConfig.cmake
        FILES ${CMAKE_CURRENT_BINARY_DIR}/warnConfigVersion.cmake
        DESTINATION ${CMAKE_INSTALL_DATADIR}/warn
    )
endif()
