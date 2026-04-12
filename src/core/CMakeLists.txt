add_library(openturbine_core SHARED
    aerodynamics/bem_solver.cpp
    aerodynamics/airfoil.cpp
    aerodynamics/wake_model.cpp
    structural/beam_solver.cpp
    structural/fatigue.cpp
    control/pid_controller.cpp
    environmental/wind_field.cpp
    environmental/turbulence.cpp
    core_types.cpp
)

set_target_properties(openturbine_core PROPERTIES
    WINDOWS_EXPORT_ALL_SYMBOLS ON
    POSITION_INDEPENDENT_CODE ON
)

target_include_directories(openturbine_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/..
)

target_link_libraries(openturbine_core PUBLIC
    Threads::Threads
)