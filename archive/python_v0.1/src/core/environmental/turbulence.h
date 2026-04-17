#pragma once

#include <vector>
#include <string>

namespace openturbine {

class TurbulenceModel {
public:
    TurbulenceModel();
    
    void set_parameters(double mean_speed, double ti, double length_scale);
    void set_model_type(const std::string& type);
    
    double compute_turbulent_velocity(double time, double longitudinal_position);
    std::vector<double> compute_velocity_deficit(double x, double y, double z);
    
    double get_turbulence_intensity() const { return turbulence_intensity_; }
    double get_length_scale() const { return length_scale_; }

private:
    double mean_wind_speed_ = 8.0;
    double turbulence_intensity_ = 0.14;
    double length_scale_ = 340.2;
    std::string model_type_ = "kaimal";
    
    double kaimal(double f);
    double von_karman(double f);
    double iec_coherence(double f, double delta);
};

class WindCoherence {
public:
    WindCoherence();
    
    void set_coherence_model(const std::string& model);
    void set_decay_coefficient(double c);
    
    double compute_coherence(double f, double delta);
    double compute_coherence_matrix(int num_points, double delta);

private:
    std::string coherence_model_ = "ieee";
    double decay_coefficient_ = 0.0;
};

}
