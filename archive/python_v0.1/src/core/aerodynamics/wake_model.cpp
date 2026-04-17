#include "wake_model.h"
#include <cmath>
#include <algorithm>

namespace openturbine {

WakeModel::WakeModel() {
}

void WakeModel::calculate_wake_field(double downstream_distance) {
    wake_field_.clear();
    
    int num_points = 50;
    double wake_length = std::min(20.0 * rotor_diameter_, downstream_distance);
    
    for (int i = 0; i < num_points; ++i) {
        double x = rotor_diameter_ * 0.5 + wake_length * i / num_points;
        
        double width = get_wake_expansion_factor(x) * rotor_diameter_ / 2.0;
        
        int radial_points = 10;
        for (int j = 0; j < radial_points; ++j) {
            double r_norm = static_cast<double>(j) / (radial_points - 1);
            double r = width * r_norm;
            
            WakePoint point;
            point.x = x;
            point.y = 0.0;
            point.z = r;
            
            point.velocity_deficit = get_centerline_velocity_deficit(x) * 
                                    std::exp(-3.0 * (r / width) * (r / width));
            point.vx = wind_speed_ * (1.0 - point.velocity_deficit);
            point.vy = 0.0;
            point.vz = 0.0;
            
            point.turbulence_intensity = turbulence_intensity_ * 
                                        (1.0 + 0.1 * x / rotor_diameter_);
            
            wake_field_.push_back(point);
        }
    }
}

double WakeModel::get_velocity_deficit_at(double x, double y, double z) const {
    if (wake_field_.empty() || x < rotor_diameter_ * 0.5) {
        return 0.0;
    }
    
    double width = get_wake_expansion_factor(x) * rotor_diameter_ / 2.0;
    double r = std::sqrt(y * y + z * z);
    
    return get_centerline_velocity_deficit(x) * std::exp(-3.0 * (r / width) * (r / width));
}

double WakeModel::get_turbulence_at(double x, double y, double z) const {
    if (wake_field_.empty() || x < rotor_diameter_ * 0.5) {
        return turbulence_intensity_;
    }
    
    return turbulence_intensity_ * (1.0 + 0.1 * x / rotor_diameter_);
}

double WakeModel::get_wake_expansion_factor(double x) const {
    if (model_type_ == "jensen") {
        return jensen_wake_width(x);
    }
    return frandsen_wake_width(x);
}

double WakeModel::get_centerline_velocity_deficit(double x) const {
    if (model_type_ == "jensen") {
        return jensen_velocity_deficit(x, 0.0);
    }
    return frandsen_velocity_deficit(x, 0.0);
}

double WakeModel::jensen_velocity_deficit(double x, double r) const {
    double k = 0.04;
    double wake_width = jensen_wake_width(x);
    
    if (wake_width <= 0.0) {
        return 0.0;
    }
    
    double deficit = ct_ / (8.0 * k * k * x * x / (rotor_diameter_ * rotor_diameter_) + 1.0);
    
    return std::max(0.0, std::min(deficit, 1.0));
}

double WakeModel::jensen_wake_width(double x) const {
    double k = 0.04;
    return 1.0 + k * x / rotor_diameter_;
}

double WakeModel::frandsen_velocity_deficit(double x, double r) const {
    if (x <= 0.0) {
        return 0.0;
    }
    
    double alpha = 0.001;
    double beta = 0.5;
    
    double deficit = ct_ / (2.0 * (1.0 + alpha * x / rotor_diameter_) * 
                           (1.0 + beta * x / rotor_diameter_));
    
    return std::max(0.0, std::min(deficit, 1.0));
}

double WakeModel::frandsen_wake_width(double x) const {
    double alpha = 0.001;
    return 1.0 + alpha * x / rotor_diameter_;
}

WakeSolver::WakeSolver() {
}

void WakeSolver::add_turbine(const std::vector<double>& position,
                             double rotor_diameter,
                             double ct,
                             double turbulence_intensity) {
    Turbine turbine;
    turbine.position = position;
    turbine.rotor_diameter = rotor_diameter;
    turbine.ct = ct;
    turbine.turbulence_intensity = turbulence_intensity;
    turbines_.push_back(turbine);
}

void WakeSolver::calculate_wake_interaction() {
    for (auto& turbine : turbines_) {
        WakeModel wake;
        wake.set_rotor_diameter(turbine.rotor_diameter);
        wake.set_wind_speed(wind_speed_);
        wake.set_thrust_coefficient(turbine.ct);
        wake.set_turbulence_intensity(turbine.turbulence_intensity);
        wake.set_model_type("jensen");
        
        wake.calculate_wake_field(20.0 * turbine.rotor_diameter);
        turbine.wake_field = wake.get_wake_field();
    }
}

double WakeSolver::get_velocity_at(double x, double y, double z) const {
    double velocity = wind_speed_;
    
    for (const auto& turbine : turbines_) {
        double dx = x - turbine.position[0];
        double dy = y - turbine.position[1];
        double dz = z - turbine.position[2];
        
        if (dx > 0) {
            double dist = std::sqrt(dx * dx + dy * dy + dz * dz);
            if (dist > 0) {
                WakeModel wake;
                wake.set_rotor_diameter(turbine.rotor_diameter);
                wake.set_thrust_coefficient(turbine.ct);
                
                double deficit = wake.get_velocity_deficit_at(dx, dy, dz);
                velocity *= (1.0 - deficit);
            }
        }
    }
    
    return std::max(0.0, velocity);
}

std::vector<double> WakeSolver::get_velocity_vector(double x, double y, double z) const {
    double wind_rad = wind_direction_ * M_PI / 180.0;
    
    return {wind_speed_ * std::cos(wind_rad),
            wind_speed_ * std::sin(wind_rad),
            0.0};
}

}
