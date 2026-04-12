#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../core/core_types.h"

namespace py = pybind11;
namespace op = openturbine;

PYBIND11_MODULE(openturbine_core, m) {
    m.doc() = "OpenTurbine C++ core module";

    py::class_<op::TurbineConfig>(m, "TurbineConfig")
        .def(py::init<>())
        .def_readwrite("rotor_diameter", &op::TurbineConfig::rotor_diameter)
        .def_readwrite("hub_height", &op::TurbineConfig::hub_height)
        .def_readwrite("num_blades", &op::TurbineConfig::num_blades)
        .def_readwrite("rated_power", &op::TurbineConfig::rated_power)
        .def_readwrite("rotor_orientation", &op::TurbineConfig::rotor_orientation)
        .def_readwrite("cone_angle", &op::TurbineConfig::cone_angle);

    py::class_<op::AerodynamicConfig>(m, "AerodynamicConfig")
        .def(py::init<>())
        .def_readwrite("blade_length", &op::AerodynamicConfig::blade_length)
        .def_readwrite("cut_in_wind_speed", &op::AerodynamicConfig::cut_in_wind_speed)
        .def_readwrite("rated_wind_speed", &op::AerodynamicConfig::rated_wind_speed)
        .def_readwrite("cut_out_wind_speed", &op::AerodynamicConfig::cut_out_wind_speed)
        .def_readwrite("cp_max", &op::AerodynamicConfig::cp_max)
        .def_readwrite("tsr_optimal", &op::AerodynamicConfig::tsr_optimal);

    py::class_<op::StructuralConfig>(m, "StructuralConfig")
        .def(py::init<>())
        .def_readwrite("blade_density", &op::StructuralConfig::blade_density)
        .def_readwrite("blade_young_modulus", &op::StructuralConfig::blade_young_modulus)
        .def_readwrite("tower_density", &op::StructuralConfig::tower_density);

    py::class_<op::ControlConfig>(m, "ControlConfig")
        .def(py::init<>())
        .def_readwrite("pitch_kp", &op::ControlConfig::pitch_kp)
        .def_readwrite("pitch_ki", &op::ControlConfig::pitch_ki)
        .def_readwrite("min_pitch_rate", &op::ControlConfig::min_pitch_rate)
        .def_readwrite("max_pitch_rate", &op::ControlConfig::max_pitch_rate);

    py::class_<op::EnvironmentConfig>(m, "EnvironmentConfig")
        .def(py::init<>())
        .def_readwrite("wind_speed_mode", &op::EnvironmentConfig::wind_speed_mode)
        .def_readwrite("constant_wind_speed", &op::EnvironmentConfig::constant_wind_speed)
        .def_readwrite("mean_wind_speed", &op::EnvironmentConfig::mean_wind_speed)
        .def_readwrite("turbulence_intensity", &op::EnvironmentConfig::turbulence_intensity)
        .def_readwrite("air_density", &op::EnvironmentConfig::air_density);

    py::class_<op::SimulationConfig>(m, "SimulationConfig")
        .def(py::init<>())
        .def_readwrite("simulation_type", &op::SimulationConfig::simulation_type)
        .def_readwrite("duration", &op::SimulationConfig::duration)
        .def_readwrite("time_step", &op::SimulationConfig::time_step);

    py::class_<op::SimulationResult>(m, "SimulationResult")
        .def(py::init<>())
        .def_readwrite("wind_speed", &op::SimulationResult::wind_speed)
        .def_readwrite("rotor_rpm", &op::SimulationResult::rotor_rpm)
        .def_readwrite("power_output", &op::SimulationResult::power_output)
        .def_readwrite("thrust_force", &op::SimulationResult::thrust_force)
        .def_readwrite("power_coefficient", &op::SimulationResult::power_coefficient)
        .def_readwrite("thrust_coefficient", &op::SimulationResult::thrust_coefficient)
        .def_readwrite("pitch_angle", &op::SimulationResult::pitch_angle)
        .def_readwrite("tip_speed_ratio", &op::SimulationResult::tip_speed_ratio);

    py::class_<op::WindTurbineSimulation>(m, "WindTurbineSimulation")
        .def(py::init<>())
        .def(py::init<const op::TurbineConfig&,
                       const op::AerodynamicConfig&,
                       const op::StructuralConfig&,
                       const op::ControlConfig&,
                       const op::EnvironmentConfig&,
                       const op::SimulationConfig&>())
        .def("initialize", &op::WindTurbineSimulation::initialize)
        .def("run_steady_state", &op::WindTurbineSimulation::run_steady_state,
             py::arg("wind_speed"))
        .def("run_time_domain", &op::WindTurbineSimulation::run_time_domain,
             py::arg("duration"))
        .def("run_parametric_sweep", &op::WindTurbineSimulation::run_parametric_sweep)
        .def("calculate_power_coefficient", &op::WindTurbineSimulation::calculate_power_coefficient,
             py::arg("tsr"), py::arg("pitch"))
        .def("calculate_thrust_coefficient", &op::WindTurbineSimulation::calculate_thrust_coefficient,
             py::arg("tsr"), py::arg("pitch"))
        .def("get_blade_angle", &op::WindTurbineSimulation::get_blade_angle,
             py::arg("time"));
}
