#pragma once

#include <vector>
#include <string>
#include <random>

namespace openturbine {

class WindFieldGenerator {
public:
    WindFieldGenerator();
    
    void set_mean_wind_speed(double speed);
    void set_wind_direction(double direction);
    void set_turbulence_intensity(double ti);
    void set_length_scale(double length);
    void set_height(double height);
    void set_shear_exponent(double alpha);
    
    void set_time_step(double dt);
    void set_seed(int seed);
    
    double generate_wind_speed(double time);
    double generate_with_shear(double time, double height);
    
    double get_wind_speed(double time, double height = 90.0);
    std::vector<double> get_wind_vector(double time, double height = 90.0);
    
    void enable_turbulence(bool enable) { turbulence_enabled_ = enable; }
    void set_turbulence_model(const std::string& model) { turbulence_model_ = model; }

private:
    double mean_wind_speed_ = 8.0;
    double wind_direction_ = 0.0;
    double turbulence_intensity_ = 0.14;
    double length_scale_ = 340.2;
    double height_ = 90.0;
    double shear_exponent_ = 0.14;
    
    double time_step_ = 0.05;
    int random_seed_ = 42;
    bool turbulence_enabled_ = true;
    std::string turbulence_model_ = "kaimal";
    
    std::mt19937 rng_;
    std::normal_distribution<double> normal_dist_;
    
    double kaimal_turbulence(double time, double dt);
    double von_karman_turbulence(double time, double dt);
    double apply_shear(double wind_speed, double height);
};

class TurbulentWindGenerator {
public:
    TurbulentWindGenerator();
    
    void set_parameters(double mean_speed, double ti, double length_scale, int seed);
    void generate_time_series(double duration, double dt);
    
    std::vector<double> get_time_series() const { return time_series_; }
    std::vector<double> get_times() const { return times_; }
    double get_mean() const;
    double get_standard_deviation() const;
    double get_turbulence_intensity() const;
    
private:
    double mean_wind_speed_ = 8.0;
    double turbulence_intensity_ = 0.14;
    double length_scale_ = 340.2;
    int seed_ = 42;
    
    std::vector<double> time_series_;
    std::vector<double> times_;
    
    std::mt19937 rng_;
    
    void kaimal_spectrum(double duration, double dt);
    void von_karman_spectrum(double duration, double dt);
};

class GustGenerator {
public:
    GustGenerator();
    
    void set_gust_type(const std::string& type);
    void set_amplitude(double amp);
    void set_duration(double dur);
    void set_direction_change(double delta_dir);
    
    double compute_gust(double time, double base_wind_speed);

private:
    std::string gust_type_ = "eog";
    double amplitude_ = 21.0;
    double duration_ = 10.0;
    double direction_change_ = 180.0;
    
    double eog_gust(double time);
    double ecd_gust(double time);
    double edg_gust(double time);
};

}
