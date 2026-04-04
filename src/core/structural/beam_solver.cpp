#include "beam_solver.h"
#include <algorithm>
#include <cmath>

namespace openturbine {

BeamSolver::BeamSolver() {
    deflection_.resize(num_points_, 0.0);
    stress_.resize(num_points_, 0.0);
}

void BeamSolver::set_length(double length) {
    length_ = length;
}

void BeamSolver::set_young_modulus(double e) {
    young_modulus_ = e;
}

void BeamSolver::set_moment_of_inertia(double i) {
    moment_of_inertia_ = i;
}

void BeamSolver::set_density(double rho) {
    density_ = rho;
}

void BeamSolver::set_area(double a) {
    area_ = a;
}

void BeamSolver::set_boundary_condition(const std::string& bc) {
    boundary_condition_ = bc;
}

void BeamSolver::add_point_load(double position, double load) {
    point_load_positions_.push_back(position);
    point_loads_.push_back(load);
}

void BeamSolver::add_distributed_load(double start, double end, double intensity) {
    distributed_loads_.push_back({start, end, intensity});
}

std::vector<double> BeamSolver::solve_deflection() {
    deflection_.assign(num_points_, 0.0);
    
    double dx = length_ / (num_points_ - 1);
    
    if (boundary_condition_ == "cantilever") {
        double EI = young_modulus_ * moment_of_inertia_;
        
        for (int i = 0; i < num_points_; ++i) {
            double x = i * dx;
            double deflection = 0.0;
            
            for (size_t j = 0; j < point_loads_.size(); ++j) {
                double a = point_load_positions_[j];
                double P = point_loads_[j];
                
                if (a <= x) {
                    double Le = length_ - a;
                    deflection += P * x * x * (3.0 * Le - x) / (6.0 * EI);
                }
            }
            
            for (const auto& dl : distributed_loads_) {
                double w = dl.intensity;
                double a = dl.start;
                double b = dl.end;
                
                if (b <= x) {
                    double Fa = w * (b - a);
                    double Ga = w * (b * b - a * a) / 2.0;
                    double Ha = w * (b * b * b - a * a * a) / 3.0;
                    deflection += (Fa * x * x * (3.0 * length_ - x) - 
                                  Ga * x * x + Ha * x) / (6.0 * EI);
                } else if (a <= x && x <= b) {
                    double Fa = w * (x - a);
                    double Ga = w * (x * x - a * a) / 2.0;
                    double Ha = w * (x * x * x - a * a * a) / 3.0;
                    deflection += (Fa * x * x * (3.0 * length_ - x) - 
                                  Ga * x * x + Ha * x) / (6.0 * EI);
                }
            }
            
            double weight = density_ * area_ * length_;
            deflection += weight * x * x * (6.0 * length_ * length_ - 
                                            4.0 * length_ * x + x * x) / (24.0 * EI);
            
            deflection_[i] = deflection;
        }
    }
    
    return deflection_;
}

std::vector<double> BeamSolver::solve_stress() {
    std::vector<double> moment = solve_moment();
    stress_.assign(num_points_, 0.0);
    
    double c = std::sqrt(moment_of_inertia_ / area_) / 2.0;
    
    for (size_t i = 0; i < moment.size(); ++i) {
        stress_[i] = std::abs(moment[i] * c / moment_of_inertia_);
    }
    
    return stress_;
}

std::vector<double> BeamSolver::solve_slope() {
    std::vector<double> deflection = solve_deflection();
    std::vector<double> slope(num_points_, 0.0);
    
    for (int i = 1; i < num_points_ - 1; ++i) {
        slope[i] = (deflection[i + 1] - deflection[i - 1]) / 2.0;
    }
    
    return slope;
}

std::vector<double> BeamSolver::solve_moment() {
    std::vector<double> moment(num_points_, 0.0);
    double dx = length_ / (num_points_ - 1);
    
    for (size_t i = 0; i < point_loads_.size(); ++i) {
        double P = point_loads_[i];
        double a = point_load_positions_[i];
        
        for (int j = 0; j < num_points_; ++j) {
            double x = j * dx;
            if (x >= a) {
                moment[j] += P * (length_ - a);
            }
        }
    }
    
    for (const auto& dl : distributed_loads_) {
        double w = dl.intensity;
        double a = dl.start;
        double b = dl.end;
        
        for (int j = 0; j < num_points_; ++j) {
            double x = j * dx;
            if (x >= a && x <= b) {
                moment[j] += w * (b - x) * (b - x) / 2.0;
            } else if (x > b) {
                moment[j] += 0.0;
            }
        }
    }
    
    return moment;
}

std::vector<double> BeamSolver::solve_shear() {
    std::vector<double> moment = solve_moment();
    std::vector<double> shear(num_points_, 0.0);
    double dx = length_ / (num_points_ - 1);
    
    for (int i = 1; i < num_points_ - 1; ++i) {
        shear[i] = -(moment[i + 1] - moment[i - 1]) / (2.0 * dx);
    }
    
    return shear;
}

ModalResult BeamSolver::calculate_first_mode() {
    ModalResult result;
    
    double EI = young_modulus_ * moment_of_inertia_;
    double rhoA = density_ * area_;
    
    if (boundary_condition_ == "cantilever") {
        double beta1 = 1.875104 / length_;
        result.frequency = beta1 * beta1 * std::sqrt(EI / rhoA) / (2.0 * M_PI);
        result.description = "First bending mode (cantilever)";
    } else {
        double beta1 = 4.730040 / length_;
        result.frequency = beta1 * beta1 * std::sqrt(EI / rhoA) / (2.0 * M_PI);
        result.description = "First bending mode (simply supported)";
    }
    
    result.mode_shape.resize(num_points_);
    for (int i = 0; i < num_points_; ++i) {
        double x = static_cast<double>(i) / (num_points_ - 1);
        result.mode_shape[i] = std::sin(M_PI * x / 2.0);
    }
    
    return result;
}

std::vector<ModalResult> BeamSolver::calculate_modes(int num_modes) {
    std::vector<ModalResult> modes;
    
    double EI = young_modulus_ * moment_of_inertia_;
    double rhoA = density_ * area_;
    
    for (int n = 1; n <= num_modes; ++n) {
        ModalResult mode;
        
        if (boundary_condition_ == "cantilever") {
            double beta_n = (2.0 * n - 1) * M_PI / (2.0 * length_);
            mode.frequency = beta_n * beta_n * std::sqrt(EI / rhoA) / (2.0 * M_PI);
        } else {
            double beta_n = n * M_PI / length_;
            mode.frequency = beta_n * beta_n * std::sqrt(EI / rhoA) / (2.0 * M_PI);
        }
        
        mode.mode_shape.resize(num_points_);
        for (int i = 0; i < num_points_; ++i) {
            double x = static_cast<double>(i) / (num_points_ - 1);
            mode.mode_shape[i] = std::sin(n * M_PI * x);
        }
        
        mode.description = "Mode " + std::to_string(n);
        modes.push_back(mode);
    }
    
    return modes;
}

double BeamSolver::get_max_deflection() const {
    return *std::max_element(deflection_.begin(), deflection_.end());
}

double BeamSolver::get_max_stress() const {
    return *std::max_element(stress_.begin(), stress_.end());
}

double BeamSolver::get_first_frequency() const {
    return calculate_first_mode().frequency;
}

BladeStructuralModel::BladeStructuralModel() {
}

void BladeStructuralModel::set_blade_length(double length) {
    blade_length_ = length;
}

void BladeStructuralModel::set_chord_distribution(const std::vector<double>& chord) {
    chord_ = chord;
}

void BladeStructuralModel::set_twist_distribution(const std::vector<double>& twist) {
    twist_ = twist;
}

void BladeStructuralModel::set_material_properties(double density, double young_modulus, double poisson) {
    density_ = density;
    young_modulus_ = young_modulus;
    poisson_ratio_ = poisson;
}

void BladeStructuralModel::calculate_mass_matrix() {
    blade_mass_.resize(chord_.size(), 0.0);
    total_mass_ = 0.0;
    
    for (size_t i = 0; i < chord_.size(); ++i) {
        double chord_val = chord_[i];
        double thickness = chord_val * 0.1;
        double length_section = blade_length_ / (chord_.size() - 1);
        
        double volume = chord_val * thickness * length_section;
        blade_mass_[i] = density_ * volume;
        total_mass_ += blade_mass_[i];
    }
    
    center_of_mass_ = 0.0;
    double moment = 0.0;
    for (size_t i = 0; i < chord_.size(); ++i) {
        double r = blade_length_ * i / (chord_.size() - 1);
        moment += blade_mass_[i] * r;
    }
    if (total_mass_ > 0.0) {
        center_of_mass_ = moment / total_mass_;
    }
}

void BladeStructuralModel::calculate_stiffness_matrix() {
}

std::vector<double> BladeStructuralModel::get_blade_mass() const {
    return blade_mass_;
}

std::vector<double> BladeStructuralModel::get_center_of_mass() const {
    std::vector<double> com(chord_.size(), 0.0);
    for (size_t i = 0; i < chord_.size(); ++i) {
        com[i] = blade_length_ * i / (chord_.size() - 1);
    }
    return com;
}

double BladeStructuralModel::get_total_mass() const {
    return total_mass_;
}

double BladeStructuralModel::get_first_bending_frequency() const {
    return first_flap_frequency_;
}

double BladeStructuralModel::get_first_edge_frequency() const {
    return first_edge_frequency_;
}

StressResult BladeStructuralModel::calculate_stress(const std::vector<double>& loads, double thrust) {
    StressResult result;
    result.max_stress.resize(chord_.size(), 0.0);
    result.von_mises.resize(chord_.size(), 0.0);
    
    double I = 0.0;
    for (size_t i = 0; i < chord_.size(); ++i) {
        double c = chord_[i] / 2.0;
        double thickness = c * 0.1;
        I += c * thickness * thickness * thickness / 12.0;
    }
    
    for (size_t i = 0; i < chord_.size(); ++i) {
        double r = blade_length_ * i / (chord_.size() - 1);
        double moment = thrust * r;
        double c = chord_[i] / 2.0;
        
        result.max_stress[i] = std::abs(moment * c / (young_modulus_ * I));
        result.von_mises[i] = result.max_stress[i];
    }
    
    result.safety_factor = 2.0;
    result.is_valid = true;
    
    return result;
}

std::vector<double> BladeStructuralModel::calculate_deflection(double thrust, double torque) {
    std::vector<double> deflection(chord_.size(), 0.0);
    
    BeamSolver solver;
    solver.set_length(blade_length_);
    solver.set_young_modulus(young_modulus_);
    solver.set_moment_of_inertia(1e-4);
    solver.set_density(density_);
    solver.set_area(0.1);
    solver.set_boundary_condition("cantilever");
    solver.add_point_load(blade_length_, thrust);
    
    deflection = solver.solve_deflection();
    
    return deflection;
}

}
