#pragma once

#include <vector>
#include <string>
#include <memory>

namespace openturbine {

struct TurbineConfig {
    double rotor_diameter = 126.0;
    double hub_height = 90.0;
    int num_blades = 3;
    double rated_power = 5e6;
    std::string rotor_orientation = "upwind";
    double cone_angle = 2.5;
    
    double tower_height = 90.0;
    double tower_base_diameter = 6.0;
    double tower_top_diameter = 3.5;
    double tower_density = 8500.0;
    
    double nacelle_mass = 50000.0;
    double hub_mass = 28000.0;
};

struct AerodynamicConfig {
    double blade_length = 61.5;
    std::vector<double> chord_distribution;
    std::vector<double> twist_distribution;
    
    std::string root_airfoil = "cylinder";
    std::string mid_airfoil = "naca63_418";
    std::string tip_airfoil = "naca64_418";
    double reynolds_number = 3e6;
    
    double cut_in_wind_speed = 3.0;
    double rated_wind_speed = 11.4;
    double cut_out_wind_speed = 25.0;
    double max_tip_speed = 80.0;
    double max_rotor_rpm = 12.1;
    
    double cp_max = 0.42;
    double tsr_optimal = 7.55;
    double ct_rated = 0.80;
    
    bool use_prandtl_tip_loss = true;
    bool use_prandtl_hub_loss = true;
    bool use_glauert_correction = true;
    int induction_iterations = 100;
    double induction_tolerance = 1e-6;
};

struct StructuralConfig {
    double blade_density = 3450.0;
    double blade_young_modulus = 40e9;
    double blade_poisson_ratio = 0.3;
    double first_bending_freq = 0.82;
    double second_bending_freq = 2.5;
    double edge_freq = 1.0;
    
    double tower_density = 8500.0;
    double tower_young_modulus = 210e9;
    double tower_yield_strength = 345e6;
    double first_tower_freq = 0.32;
    
    double gearbox_ratio = 97.0;
    double generator_inertia = 534.116;
    double lss_damping = 27.78;
    
    double safety_factor = 1.5;
    double blade_safety_factor = 2.0;
    double tower_safety_factor = 1.5;
    
    double sn_curve_slope = 10.0;
    double sn_curve_intercept = 1e8;
};

struct ControlConfig {
    double pitch_kp = 0.018;
    double pitch_ki = 0.002;
    double pitch_kd = 0.0;
    double min_pitch_rate = -8.0;
    double max_pitch_rate = 8.0;
    double min_pitch_angle = 0.0;
    double max_pitch_angle = 90.0;
    double rated_pitch_angle = 2.0;
    
    bool yaw_enabled = true;
    double yaw_kp = 0.001;
    double yaw_ki = 0.0001;
    double max_yaw_rate = 0.5;
    double max_yaw_error = 8.0;
    
    std::string torque_control_type = "quadratic";
    double torque_kp = 50.0;
    double torque_ki = 5.0;
    double rated_torque = 41000.0;
    double rated_rpm = 1173.7;
    double cut_in_rpm = 700.0;
    
    double region2_start = 3.0;
    double region2_5_start = 11.4;
    double emergency_pitch_rate = 15.0;
    double overspeed_threshold = 1.1;
};

struct EnvironmentConfig {
    std::string wind_speed_mode = "weibull";
    double constant_wind_speed = 8.0;
    double mean_wind_speed = 8.0;
    double weibull_shape = 2.0;
    double weibull_scale = 9.0;
    double wind_speed_min = 0.0;
    double wind_speed_max = 30.0;
    
    bool turbulence_enabled = true;
    std::string turbulence_model = "kaimal";
    double turbulence_intensity = 0.14;
    double turbulence_length_scale = 340.2;
    
    bool wind_shear_enabled = true;
    std::string shear_law = "power";
    double shear_exponent = 0.14;
    double roughness_length = 0.03;
    double reference_height = 90.0;
    
    double air_density = 1.225;
    double temperature = 15.0;
    double pressure = 101325.0;
    
    bool gust_enabled = true;
    double eog_gust_speed = 21.0;
    double eog_gust_duration = 10.0;
    
    std::string terrain_type = "offshore";
    double terrain_roughness = 0.0002;
    
    double simulation_time_step = 0.05;
    int random_seed = 42;
};

struct SimulationConfig {
    std::string simulation_type = "steady_state";
    double duration = 600.0;
    double time_step = 0.01;
    
    bool wind_sweep_enabled = true;
    double sweep_start = 3.0;
    double sweep_end = 25.0;
    double sweep_step = 1.0;
    
    bool save_results = true;
    std::string results_directory = "results";
    std::vector<std::string> export_formats = {"csv", "json"};
};

struct SimulationResult {
    double wind_speed;
    double rotor_rpm;
    double power_output;
    double thrust_force;
    double power_coefficient;
    double thrust_coefficient;
    double pitch_angle;
    double tip_speed_ratio;
    double aerodynamic_efficiency;
    
    std::vector<double> blade_loads;
    std::vector<double> blade_deflections;
    std::vector<double> tower_deflection;
    
    std::vector<double> time_series_power;
    std::vector<double> time_series_rpm;
    std::vector<double> time_series_thrust;
    std::vector<double> time_series_pitch;
};

class WindTurbineSimulation {
public:
    WindTurbineSimulation();
    explicit WindTurbineSimulation(
        const TurbineConfig& turbine,
        const AerodynamicConfig& aero,
        const StructuralConfig& structural,
        const ControlConfig& control,
        const EnvironmentConfig& env,
        const SimulationConfig& sim
    );
    
    void set_turbine_config(const TurbineConfig& config);
    void set_aerodynamic_config(const AerodynamicConfig& config);
    void set_structural_config(const StructuralConfig& config);
    void set_control_config(const ControlConfig& config);
    void set_environment_config(const EnvironmentConfig& config);
    void set_simulation_config(const SimulationConfig& config);
    
    const TurbineConfig& get_turbine_config() const { return turbine_config_; }
    const AerodynamicConfig& get_aerodynamic_config() const { return aero_config_; }
    const StructuralConfig& get_structural_config() const { return structural_config_; }
    const ControlConfig& get_control_config() const { return control_config_; }
    const EnvironmentConfig& get_environment_config() const { return env_config_; }
    const SimulationConfig& get_simulation_config() const { return sim_config_; }
    
    void initialize();
    SimulationResult run_steady_state(double wind_speed);
    SimulationResult run_time_domain(double duration);
    std::vector<SimulationResult> run_parametric_sweep();
    
    double calculate_power_coefficient(double tsr, double pitch);
    double calculate_thrust_coefficient(double tsr, double pitch);
    double calculate_power(double wind_speed, double tsr, double pitch);
    double calculate_rotor_rpm(double wind_speed, double tsr);
    
    void update_animation_state(double time);
    double get_blade_angle(double time) const;
    double get_blade_tip_position(int blade, double time) const;

private:
    TurbineConfig turbine_config_;
    AerodynamicConfig aero_config_;
    StructuralConfig structural_config_;
    ControlConfig control_config_;
    EnvironmentConfig env_config_;
    SimulationConfig sim_config_;
    
    bool initialized_ = false;
    double current_time_ = 0.0;
    double current_rotor_angle_ = 0.0;
    
    double solve_induction_factor(double tsr, double pitch);
    double get_airfoil_lift_coefficient(double angle_of_attack, double reynolds);
    double get_airfoil_drag_coefficient(double angle_of_attack, double reynolds);
};

}
