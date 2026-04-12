#pragma once

#include <vector>
#include <string>

namespace openturbine {

struct ModalResult {
    double frequency;
    std::vector<double> mode_shape;
    std::string description;
};

struct StressResult {
    std::vector<double> max_stress;
    std::vector<double> von_mises;
    double safety_factor;
    bool is_valid;
};

class BeamSolver {
public:
    BeamSolver();
    
    void set_length(double length);
    void set_young_modulus(double e);
    void set_moment_of_inertia(double i);
    void set_density(double rho);
    void set_area(double a);
    void set_boundary_condition(const std::string& bc);
    
    void add_point_load(double position, double load);
    void add_distributed_load(double start, double end, double intensity);
    
    std::vector<double> solve_deflection();
    std::vector<double> solve_stress();
    std::vector<double> solve_slope();
    std::vector<double> solve_moment();
    std::vector<double> solve_shear();
    
    ModalResult calculate_first_mode() const;
    std::vector<ModalResult> calculate_modes(int num_modes);
    
    double get_max_deflection() const;
    double get_max_stress() const;
    double get_first_frequency() const;

private:
    double length_ = 1.0;
    double young_modulus_ = 210e9;
    double moment_of_inertia_ = 1e-4;
    double density_ = 7850.0;
    double area_ = 1e-3;
    std::string boundary_condition_ = "cantilever";
    
    std::vector<double> point_loads_;
    std::vector<double> point_load_positions_;
    
    struct DistributedLoad {
        double start, end, intensity;
    };
    std::vector<DistributedLoad> distributed_loads_;
    
    std::vector<double> deflection_;
    std::vector<double> stress_;
    
    int num_points_ = 100;
};

class BladeStructuralModel {
public:
    BladeStructuralModel();
    
    void set_blade_length(double length);
    void set_chord_distribution(const std::vector<double>& chord);
    void set_twist_distribution(const std::vector<double>& twist);
    void set_material_properties(double density, double young_modulus, double poisson);
    
    void calculate_mass_matrix();
    void calculate_stiffness_matrix();
    
    std::vector<double> get_blade_mass() const;
    std::vector<double> get_center_of_mass() const;
    double get_total_mass() const;
    double get_first_bending_frequency() const;
    double get_first_edge_frequency() const;
    
    StressResult calculate_stress(const std::vector<double>& loads, double thrust);
    std::vector<double> calculate_deflection(double thrust, double torque);

private:
    double blade_length_ = 61.5;
    std::vector<double> chord_;
    std::vector<double> twist_;
    
    double density_ = 3450.0;
    double young_modulus_ = 40e9;
    double poisson_ratio_ = 0.3;
    
    std::vector<double> mass_matrix_;
    std::vector<double> stiffness_matrix_;
    
    std::vector<double> blade_mass_;
    double total_mass_;
    double center_of_mass_;
    
    double first_flap_frequency_ = 0.0;
    double first_edge_frequency_ = 0.0;
};

}
