#include "core_types.h"
#include <cmath>
#include <algorithm>

namespace openturbine {

WindTurbineSimulation::WindTurbineSimulation()
    : turbine_config_(TurbineConfig())
    , aero_config_(AerodynamicConfig())
    , structural_config_(StructuralConfig())
    , control_config_(ControlConfig())
    , env_config_(EnvironmentConfig())
    , sim_config_(SimulationConfig())
{
}

WindTurbineSimulation::WindTurbineSimulation(
    const TurbineConfig& turbine,
    const AerodynamicConfig& aero,
    const StructuralConfig& structural,
    const ControlConfig& control,
    const EnvironmentConfig& env,
    const SimulationConfig& sim)
    : turbine_config_(turbine)
    , aero_config_(aero)
    , structural_config_(structural)
    , control_config_(control)
    , env_config_(env)
    , sim_config_(sim)
{
    initialize();
}

void WindTurbineSimulation::set_turbine_config(const TurbineConfig& config) {
    turbine_config_ = config;
    initialized_ = false;
}

void WindTurbineSimulation::set_aerodynamic_config(const AerodynamicConfig& config) {
    aero_config_ = config;
    initialized_ = false;
}

void WindTurbineSimulation::set_structural_config(const StructuralConfig& config) {
    structural_config_ = config;
}

void WindTurbineSimulation::set_control_config(const ControlConfig& config) {
    control_config_ = config;
}

void WindTurbineSimulation::set_environment_config(const EnvironmentConfig& config) {
    env_config_ = config;
}

void WindTurbineSimulation::set_simulation_config(const SimulationConfig& config) {
    sim_config_ = config;
}

void WindTurbineSimulation::initialize() {
    current_time_ = 0.0;
    current_rotor_angle_ = 0.0;
    initialized_ = true;
}

SimulationResult WindTurbineSimulation::run_steady_state(double wind_speed) {
    SimulationResult result;
    result.wind_speed = wind_speed;
    
    if (wind_speed < aero_config_.cut_in_wind_speed || 
        wind_speed > aero_config_.cut_out_wind_speed) {
        result.power_output = 0.0;
        result.rotor_rpm = 0.0;
        result.thrust_force = 0.0;
        result.power_coefficient = 0.0;
        result.thrust_coefficient = 0.0;
        result.pitch_angle = 0.0;
        result.tip_speed_ratio = 0.0;
        return result;
    }
    
    double rotor_radius = turbine_config_.rotor_diameter / 2.0;
    double swept_area = M_PI * rotor_radius * rotor_radius;
    
    double pitch = control_config_.rated_pitch_angle;
    
    double tsr = aero_config_.tsr_optimal;
    if (wind_speed > aero_config_.rated_wind_speed) {
        tsr = (aero_config_.max_rotor_rpm * 2.0 * M_PI / 60.0) * rotor_radius / wind_speed;
    }
    
    double tip_speed = wind_speed * tsr;
    result.rotor_rpm = tip_speed / (2.0 * M_PI * rotor_radius) * 60.0 / 1.0;
    result.tip_speed_ratio = tsr;
    result.pitch_angle = pitch;
    
    double ct = calculate_thrust_coefficient(tsr, pitch);
    result.thrust_coefficient = ct;
    result.thrust_force = 0.5 * env_config_.air_density * swept_area * ct * wind_speed * wind_speed;
    
    double cp = calculate_power_coefficient(tsr, pitch);
    result.power_coefficient = cp;
    result.power_output = 0.5 * env_config_.air_density * swept_area * cp * std::pow(wind_speed, 3);
    result.power_output = std::min(result.power_output, turbine_config_.rated_power);
    
    result.aerodynamic_efficiency = cp / 0.59;
    
    return result;
}

SimulationResult WindTurbineSimulation::run_time_domain(double duration) {
    SimulationResult result;
    double dt = sim_config_.time_step;
    int num_steps = static_cast<int>(duration / dt);
    
    result.time_series_power.resize(num_steps);
    result.time_series_rpm.resize(num_steps);
    result.time_series_thrust.resize(num_steps);
    result.time_series_pitch.resize(num_steps);
    
    double wind_speed = env_config_.mean_wind_speed;
    
    for (int i = 0; i < num_steps; ++i) {
        double time = i * dt;
        
        double current_pitch = control_config_.rated_pitch_angle;
        if (wind_speed > aero_config_.rated_wind_speed) {
            current_pitch += 0.5 * (wind_speed - aero_config_.rated_wind_speed);
            current_pitch = std::min(current_pitch, control_config_.max_pitch_angle);
        }
        
        double rotor_radius = turbine_config_.rotor_diameter / 2.0;
        double swept_area = M_PI * rotor_radius * rotor_radius;
        double tsr = aero_config_.tsr_optimal;
        
        double tip_speed = wind_speed * tsr;
        double rpm = tip_speed / (2.0 * M_PI * rotor_radius) * 60.0;
        
        double ct = calculate_thrust_coefficient(tsr, current_pitch);
        double cp = calculate_power_coefficient(tsr, current_pitch);
        double power = 0.5 * env_config_.air_density * swept_area * cp * std::pow(wind_speed, 3);
        double thrust = 0.5 * env_config_.air_density * swept_area * ct * wind_speed * wind_speed;
        
        result.time_series_power[i] = std::min(power, turbine_config_.rated_power);
        result.time_series_rpm[i] = rpm;
        result.time_series_thrust[i] = thrust;
        result.time_series_pitch[i] = current_pitch;
        
        current_rotor_angle_ += rpm * 2.0 * M_PI / 60.0 * dt;
    }
    
    result.wind_speed = wind_speed;
    result.rotor_rpm = result.time_series_rpm.back();
    result.power_output = result.time_series_power.back();
    result.thrust_force = result.time_series_thrust.back();
    result.pitch_angle = result.time_series_pitch.back();
    
    return result;
}

std::vector<SimulationResult> WindTurbineSimulation::run_parametric_sweep() {
    std::vector<SimulationResult> results;
    
    for (double wind_speed = sim_config_.sweep_start; 
         wind_speed <= sim_config_.sweep_end; 
         wind_speed += sim_config_.sweep_step) {
        results.push_back(run_steady_state(wind_speed));
    }
    
    return results;
}

double WindTurbineSimulation::calculate_power_coefficient(double tsr, double pitch) {
    double cp = 0.0;
    
    if (tsr > 0.0 && tsr < 15.0) {
        double pitch_rad = pitch * M_PI / 180.0;
        cp = 0.22 * (116.0 / (tsr + 0.08 * pitch_rad) - 0.4 * pitch_rad - 5.0);
        cp = std::max(0.0, std::min(cp, aero_config_.cp_max));
    }
    
    return cp;
}

double WindTurbineSimulation::calculate_thrust_coefficient(double tsr, double pitch) {
    double ct = 0.0;
    
    if (tsr > 0.0 && tsr < 15.0) {
        double pitch_rad = pitch * M_PI / 180.0;
        ct = 4.0 * (1.0 - 0.09 * tsr) / (tsr + 1.0);
        ct = std::max(0.0, std::min(ct, 1.0));
    }
    
    return ct;
}

double WindTurbineSimulation::calculate_power(double wind_speed, double tsr, double pitch) {
    double rotor_radius = turbine_config_.rotor_diameter / 2.0;
    double swept_area = M_PI * rotor_radius * rotor_radius;
    double cp = calculate_power_coefficient(tsr, pitch);
    
    return 0.5 * env_config_.air_density * swept_area * cp * std::pow(wind_speed, 3);
}

double WindTurbineSimulation::calculate_rotor_rpm(double wind_speed, double tsr) {
    double rotor_radius = turbine_config_.rotor_diameter / 2.0;
    double tip_speed = wind_speed * tsr;
    return tip_speed / (2.0 * M_PI * rotor_radius) * 60.0;
}

void WindTurbineSimulation::update_animation_state(double time) {
    current_time_ = time;
    
    double wind_speed = env_config_.mean_wind_speed;
    double tsr = aero_config_.tsr_optimal;
    double rotor_radius = turbine_config_.rotor_diameter / 2.0;
    double tip_speed = wind_speed * tsr;
    double rpm = tip_speed / (2.0 * M_PI * rotor_radius) * 60.0;
    
    current_rotor_angle_ += rpm * 2.0 * M_PI / 60.0 * sim_config_.time_step;
    current_rotor_angle_ = std::fmod(current_rotor_angle_, 2.0 * M_PI);
}

double WindTurbineSimulation::get_blade_angle(double time) const {
    double wind_speed = env_config_.mean_wind_speed;
    double tsr = aero_config_.tsr_optimal;
    double rotor_radius = turbine_config_.rotor_diameter / 2.0;
    double tip_speed = wind_speed * tsr;
    double rpm = tip_speed / (2.0 * M_PI * rotor_radius) * 60.0;
    
    return rpm * 2.0 * M_PI / 60.0 * time;
}

double WindTurbineSimulation::get_blade_tip_position(int blade, double time) const {
    double blade_angle = get_blade_angle(time);
    double blade_spacing = 2.0 * M_PI / turbine_config_.num_blades;
    return blade_angle + blade_spacing * blade;
}

double WindTurbineSimulation::solve_induction_factor(double tsr, double pitch) {
    double a = 0.5;
    double tolerance = aero_config_.induction_tolerance;
    int max_iter = aero_config_.induction_iterations;
    
    for (int i = 0; i < max_iter; ++i) {
        double pitch_rad = pitch * M_PI / 180.0;
        double phi = std::atan2(1.0, tsr * (1.0 - a));
        double alpha = phi - pitch_rad;
        
        double cl = get_airfoil_lift_coefficient(alpha, aero_config_.reynolds_number);
        double cd = get_airfoil_drag_coefficient(alpha, aero_config_.reynolds_number);
        
        double cn = cl * std::cos(phi) - cd * std::sin(phi);
        double ct_new = cn / (tsr * tsr * (1.0 - a) * (1.0 - a));
        
        double a_new = ct_new / (4.0 * (1.0 - a));
        a_new = std::max(0.0, std::min(a_new, 0.5));
        
        if (std::abs(a_new - a) < tolerance) {
            return a_new;
        }
        
        a = a_new;
    }
    
    return a;
}

double WindTurbineSimulation::get_airfoil_lift_coefficient(double angle_of_attack, double reynolds) {
    double cl = 0.0;
    double aoa_deg = angle_of_attack * 180.0 / M_PI;
    
    if (aoa_deg < 15.0) {
        cl = 2.0 * M_PI * angle_of_attack;
    } else {
        cl = 0.9 * 2.0 * M_PI * std::sin(angle_of_attack);
    }
    
    return std::max(-1.5, std::min(cl, 2.0));
}

double WindTurbineSimulation::get_airfoil_drag_coefficient(double angle_of_attack, double reynolds) {
    double cd_base = 0.008;
    double aoa_deg = std::abs(angle_of_attack * 180.0 / M_PI);
    
    if (aoa_deg > 15.0) {
        cd_base += 0.001 * (aoa_deg - 15.0);
    }
    
    return cd_base;
}

}
