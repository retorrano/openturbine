find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 REQUIRED)

# Add Eigen include directory if specified
if(EIGEN3_INCLUDE_DIR)
    include_directories(${EIGEN3_INCLUDE_DIR})
endif()

pybind11_add_module(openturbine_pybind
    pybind_aerodynamics.cpp
    pybind_structural.cpp
    pybind_control.cpp
    pybind_environmental.cpp
    pybind_core.cpp
)

target_link_libraries(openturbine_pybind PRIVATE
    openturbine_core
    Python3::Python
)

set_target_properties(openturbine_pybind PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}/openturbine
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/openturbine
)
