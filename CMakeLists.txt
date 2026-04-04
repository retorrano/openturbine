cmake_minimum_required(VERSION 3.20)
project(OpenTurbine VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib)

option(BUILD_TESTS "Build tests" ON)
option(BUILD_PYTHON_BINDINGS "Build Python bindings" ON)

find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
find_package(Threads REQUIRED)

include_directories(
    ${CMAKE_SOURCE_DIR}/src/core
    ${CMAKE_BINARY_DIR}/include
)

add_subdirectory(src/core)
add_subdirectory(src/bindings)

if(BUILD_TESTS)
    enable_testing()
    add_subdirectory(tests)
endif()
