#include "bem_solver.h"
#include <algorithm>
#include <iostream>

namespace openturbine {

BEMSolver::BEMSolver() {
    local_thrust_.resize(num_stations_, 0.0);
    local_power_.resize(num_stations_, 0.0);
    local_alpha_.resize(num_stations_, 0.0);
    local_a_.resize(num_stations_, 0.0);
}

void BEMSolver::set_rotor_radius(double radius) {
    rotor_radius_ = radius;
}

void BEMSolver::set_num_blades(int num_blades) {
    num_blades_ = num_blades;
}

void BEMSolver::set_blade_data(const std::vector<double>& chord,
                                const std::vector<double>& twist,
                                const std::vector<double>& position) {
    chord_ = chord;
    twist_ = twist;
    station_ = position;
    num_stations_ = static_cast<int>(station_.size());
    
    local_thrust_.resize(num_stations_, 0.0);
    local_power_.resize(num_stations_, 0.0);
    local_alpha_.resize(num_stations_, 0.0);
    local_a_.resize(num_stations_, 0.0);
}

void BEMSolver::set_airfoil_data(const AirfoilData& airfoil) {
    airfoil_ = airfoil;
}

void BEMSolver::set_wind_speed(double wind_speed) {
    wind_speed_ = wind_speed;
}

void BEMSolver::set_tip_speed_ratio(double tsr) {
    tip_speed_ratio_ = tsr;
}

void BEMSolver::set_pitch_angle(double pitch) {
    pitch_angle_ = pitch;
}

void BEMSolver::set_air_density(double rho) {
    air_density_ = rho;
}

void BEMSolver::solve() {
    ct_ = 0.0;
    cp_ = 0.0;
    a_ = 0.0;
    double alpha_sum = 0.0;
    
    double hub_radius = 0.1 * rotor_radius_;
    double tip_radius = rotor_radius_;
    
    for (int i = 0; i < num_stations_; ++i) {
        double r = station_[i] * (tip_radius - hub_radius) + hub_radius;
        
        double lambda_r = tip_speed_ratio_ * r / rotor_radius_;
        double phi = std::atan2(1.0, lambda_r);
        
        double pitch_rad = pitch_angle_ * M_PI / 180.0;
        double twist_rad = twist_[i] * M_PI / 180.0;
        double alpha = phi - twist_rad - pitch_rad;
        
        local_alpha_[i] = alpha * 180.0 / M_PI;
        alpha_sum += alpha;
        
        double cl = interpolate_cl(alpha);
        double cd = interpolate_cd(alpha);
        
        double cn = cl * std::cos(phi) - cd * std::sin(phi);
        double ct_station = cn * chord_[i] * num_blades_ / (2.0 * M_PI * r);
        
        double f_tip = 1.0;
        if (use_tip_loss_) {
            f_tip = calculate_prandtl_tip_loss(r);
        }
        
        double f_hub = 1.0;
        if (use_hub_loss_) {
            f_hub = calculate_prandtl_hub_loss(r);
        }
        
        double f = f_tip * f_hub;
        f = std::max(0.1, std::min(f, 1.0));
        
        double a = 0.0;
        if (f > 0.1) {
            a = ct_station / (4.0 * f * std::sin(phi) * std::sin(phi));
            a = std::max(0.0, std::min(a, 0.5));
        }
        
        if (use_glauert_correction_ && a > 0.2) {
            double glauert_factor = 0.25 * (7.0 - 9.0 * a) / (1.0 - a);
            ct_station *= glauert_factor;
        }
        
        local_a_[i] = a;
        
        double relative_velocity = wind_speed_ * (1.0 - a) / std::sin(phi);
        local_thrust_[i] = 0.5 * air_density_ * relative_velocity * relative_velocity * 
                           cn * chord_[i];
        
        local_power_[i] = local_thrust_[i] * relative_velocity * std::tan(phi) * r;
        
        ct_ += local_thrust_[i];
        cp_ += local_power_[i];
    }
    
    ct_ /= (0.5 * air_density_ * M_PI * rotor_radius_ * rotor_radius_ * wind_speed_ * wind_speed_);
    cp_ /= (0.5 * air_density_ * M_PI * rotor_radius_ * rotor_radius_ * 
            std::pow(wind_speed_, 3));
    
    alpha_avg_ = alpha_sum / num_stations_ * 180.0 / M_PI;
}

double BEMSolver::interpolate_cl(double alpha) {
    if (airfoil_.alpha.empty()) {
        return 2.0 * M_PI * alpha;
    }
    
    double aoa_deg = alpha * 180.0 / M_PI;
    
    for (size_t i = 0; i < airfoil_.alpha.size() - 1; ++i) {
        if (aoa_deg >= airfoil_.alpha[i] && aoa_deg <= airfoil_.alpha[i + 1]) {
            double t = (aoa_deg - airfoil_.alpha[i]) / (airfoil_.alpha[i + 1] - airfoil_.alpha[i]);
            return airfoil_.cl[i] + t * (airfoil_.cl[i + 1] - airfoil_.cl[i]);
        }
    }
    
    if (aoa_deg < airfoil_.alpha.front()) {
        return airfoil_.cl.front();
    }
    return airfoil_.cl.back();
}

double BEMSolver::interpolate_cd(double alpha) {
    if (airfoil_.cd.empty()) {
        return 0.008;
    }
    
    double aoa_deg = alpha * 180.0 / M_PI;
    
    for (size_t i = 0; i < airfoil_.alpha.size() - 1; ++i) {
        if (aoa_deg >= airfoil_.alpha[i] && aoa_deg <= airfoil_.alpha[i + 1]) {
            double t = (aoa_deg - airfoil_.alpha[i]) / (airfoil_.alpha[i + 1] - airfoil_.alpha[i]);
            return airfoil_.cd[i] + t * (airfoil_.cd[i + 1] - airfoil_.cd[i]);
        }
    }
    
    if (aoa_deg < airfoil_.alpha.front()) {
        return airfoil_.cd.front();
    }
    return airfoil_.cd.back();
}

double BEMSolver::calculate_prandtl_tip_loss(double r) {
    double tip_speed_ratio = tip_speed_ratio_;
    double lambda = tip_speed_ratio;
    
    double phi = std::atan2(1.0, lambda * r / rotor_radius_);
    double sin_phi = std::sin(phi);
    
    if (sin_phi < 0.001) {
        return 1.0;
    }
    
    double f = 2.0 / M_PI * std::acos(std::exp(-num_blades_ / 2.0 * 
                      (rotor_radius_ - r) / (r * sin_phi)));
    
    return std::max(0.01, std::min(f, 1.0));
}

double BEMSolver::calculate_prandtl_hub_loss(double r) {
    double hub_radius = 0.1 * rotor_radius_;
    double tip_speed_ratio = tip_speed_ratio_;
    double lambda = tip_speed_ratio;
    
    double phi = std::atan2(1.0, lambda * r / rotor_radius_);
    double sin_phi = std::sin(phi);
    
    if (sin_phi < 0.001) {
        return 1.0;
    }
    
    double f = 2.0 / M_PI * std::acos(std::exp(-num_blades_ / 2.0 * 
                      (r - hub_radius) / (r * sin_phi)));
    
    return std::max(0.01, std::min(f, 1.0));
}

}
