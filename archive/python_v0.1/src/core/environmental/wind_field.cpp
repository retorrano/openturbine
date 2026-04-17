#include "wind_field.h"
#include <cmath>
#include <algorithm>

namespace openturbine {

WindFieldGenerator::WindFieldGenerator()
    : rng_(42), normal_dist_(0.0, 1.0)
{
}

void WindFieldGenerator::set_mean_wind_speed(double speed) {
    mean_wind_speed_ = speed;
}

void WindFieldGenerator::set_wind_direction(double direction) {
    wind_direction_ = direction;
}

void WindFieldGenerator::set_turbulence_intensity(double ti) {
    turbulence_intensity_ = ti;
}

void WindFieldGenerator::set_length_scale(double length) {
    length_scale_ = length;
}

void WindFieldGenerator::set_height(double height) {
    height_ = height;
}

void WindFieldGenerator::set_shear_exponent(double alpha) {
    shear_exponent_ = alpha;
}

void WindFieldGenerator::set_time_step(double dt) {
    time_step_ = dt;
}

void WindFieldGenerator::set_seed(int seed) {
    random_seed_ = seed;
    rng_.seed(seed);
}

double WindFieldGenerator::generate_wind_speed(double time) {
    if (!turbulence_enabled_) {
        return mean_wind_speed_;
    }
    
    if (turbulence_model_ == "kaimal") {
        return mean_wind_speed_ + kaimal_turbulence(time, time_step_);
    } else if (turbulence_model_ == "von_karman") {
        return mean_wind_speed_ + von_karman_turbulence(time, time_step_);
    }
    
    return mean_wind_speed_;
}

double WindFieldGenerator::generate_with_shear(double time, double target_height) {
    double base_speed = generate_wind_speed(time);
    return apply_shear(base_speed, target_height);
}

double WindFieldGenerator::get_wind_speed(double time, double target_height) {
    double speed = generate_wind_speed(time);
    return apply_shear(speed, target_height);
}

std::vector<double> WindFieldGenerator::get_wind_vector(double time, double target_height) {
    double speed = get_wind_speed(time, target_height);
    double dir_rad = wind_direction_ * M_PI / 180.0;
    
    return {
        speed * std::cos(dir_rad),
        speed * std::sin(dir_rad),
        0.0
    };
}

double WindFieldGenerator::kaimal_turbulence(double time, double dt) {
    double sigma = turbulence_intensity_ * mean_wind_speed_;
    
    double omega1 = 0.001;
    double omega2 = 1.0 / (length_scale_ / mean_wind_speed_);
    
    double phi1 = std::sqrt(2.0) * sigma * std::sqrt(omega2 - omega1) * normal_dist_(rng_);
    double phi2 = std::sqrt(2.0) * sigma * std::sqrt(omega2 - omega1) * normal_dist_(rng_);
    
    double decay = std::exp(-omega2 * time);
    double noise = sigma * std::sqrt(2.0 / (omega2 * dt)) * normal_dist_(rng_);
    
    return phi1 * decay + noise;
}

double WindFieldGenerator::von_karman_turbulence(double time, double dt) {
    double sigma = turbulence_intensity_ * mean_wind_speed_;
    
    double omega_cutoff = 1.0 / (length_scale_ / mean_wind_speed_);
    double decay = std::exp(-omega_cutoff * time);
    double noise = sigma * std::sqrt(2.0 / (omega_cutoff * dt)) * normal_dist_(rng_);
    
    return decay * noise;
}

double WindFieldGenerator::apply_shear(double wind_speed, double target_height) {
    if (target_height <= 0.0) {
        return 0.0;
    }
    
    double speed_ratio = std::pow(target_height / height_, shear_exponent_);
    return wind_speed * speed_ratio;
}

TurbulentWindGenerator::TurbulentWindGenerator()
    : rng_(42)
{
}

void TurbulentWindGenerator::set_parameters(double mean_speed, double ti, 
                                           double length_scale, int seed) {
    mean_wind_speed_ = mean_speed;
    turbulence_intensity_ = ti;
    length_scale_ = length_scale;
    seed_ = seed;
    rng_.seed(seed);
}

void TurbulentWindGenerator::generate_time_series(double duration, double dt) {
    if (turbulence_model_ == "kaimal") {
        kaimal_spectrum(duration, dt);
    } else {
        von_karman_spectrum(duration, dt);
    }
}

void TurbulentWindGenerator::kaimal_spectrum(double duration, double dt) {
    int n_samples = static_cast<int>(duration / dt);
    time_series_.resize(n_samples);
    times_.resize(n_samples);
    
    double sigma = turbulence_intensity_ * mean_wind_speed_;
    
    std::normal_distribution<double> dist(0.0, 1.0);
    
    for (int i = 0; i < n_samples; ++i) {
        times_[i] = i * dt;
        time_series_[i] = mean_wind_speed_ + sigma * dist(rng_);
    }
}

void TurbulentWindGenerator::von_karman_spectrum(double duration, double dt) {
    kaimal_spectrum(duration, dt);
}

double TurbulentWindGenerator::get_mean() const {
    if (time_series_.empty()) return 0.0;
    
    double sum = 0.0;
    for (double v : time_series_) {
        sum += v;
    }
    return sum / time_series_.size();
}

double TurbulentWindGenerator::get_standard_deviation() const {
    if (time_series_.size() < 2) return 0.0;
    
    double mean = get_mean();
    double sum_sq = 0.0;
    for (double v : time_series_) {
        sum_sq += (v - mean) * (v - mean);
    }
    return std::sqrt(sum_sq / (time_series_.size() - 1));
}

double TurbulentWindGenerator::get_turbulence_intensity() const {
    double mean = get_mean();
    if (mean <= 0.0) return 0.0;
    return get_standard_deviation() / mean;
}

GustGenerator::GustGenerator()
{
}

void GustGenerator::set_gust_type(const std::string& type) {
    gust_type_ = type;
}

void GustGenerator::set_amplitude(double amp) {
    amplitude_ = amp;
}

void GustGenerator::set_duration(double dur) {
    duration_ = dur;
}

void GustGenerator::set_direction_change(double delta_dir) {
    direction_change_ = delta_dir;
}

double GustGenerator::compute_gust(double time, double base_wind_speed) {
    if (gust_type_ == "eog") {
        return eog_gust(time);
    } else if (gust_type_ == "ecd") {
        return ecd_gust(time);
    } else if (gust_type_ == "edg") {
        return edg_gust(time);
    }
    return 0.0;
}

double GustGenerator::eog_gust(double time) {
    if (time < 0 || time > duration_) {
        return 0.0;
    }
    
    double t_gust = 1.0 - time / duration_;
    return amplitude_ * t_gust * std::sin(3.0 * M_PI * time / duration_);
}

double GustGenerator::ecd_gust(double time) {
    if (time < 0 || time > duration_) {
        return 0.0;
    }
    
    return amplitude_ * std::sin(2.0 * M_PI * time / duration_);
}

double GustGenerator::edg_gust(double time) {
    if (time < 0 || time > duration_) {
        return 0.0;
    }
    
    double t_gust = time / duration_;
    return amplitude_ * (1.0 - std::cos(2.0 * M_PI * t_gust)) / 2.0;
}

}
