#pragma once

#include <string>
#include <vector>

namespace openturbine {

class PIDController {
public:
    PIDController();
    PIDController(double kp, double ki, double kd);
    
    void set_gains(double kp, double ki, double kd);
    void set_output_limits(double min_out, double max_out);
    void set_integral_limit(double limit);
    void set_derivative_filter(double filter_coeff);
    
    double compute(double setpoint, double measurement, double dt);
    
    void reset();
    
    double get_kp() const { return kp_; }
    double get_ki() const { return ki_; }
    double get_kd() const { return kd_; }
    double get_last_output() const { return last_output_; }
    double get_integral() const { return integral_; }

private:
    double kp_ = 0.0;
    double ki_ = 0.0;
    double kd_ = 0.0;
    
    double min_output_ = -1e10;
    double max_output_ = 1e10;
    double integral_limit_ = 1e10;
    double derivative_filter_ = 0.0;
    
    double integral_ = 0.0;
    double last_error_ = 0.0;
    double last_measurement_ = 0.0;
    double last_output_ = 0.0;
    bool first_step_ = true;
};

class PitchController {
public:
    PitchController();
    PitchController(double kp, double ki, double kd);
    
    void set_gains(double kp, double ki, double kd);
    void set_pitch_limits(double min_pitch, double max_pitch);
    void set_rate_limits(double min_rate, double max_rate);
    
    double compute_pitch(double rated_rpm, double current_rpm, double dt);
    
    void set_current_pitch(double pitch) { current_pitch_ = pitch; }
    double get_current_pitch() const { return current_pitch_; }
    
private:
    PIDController pid_;
    double min_pitch_ = 0.0;
    double max_pitch_ = 90.0;
    double min_rate_ = -8.0;
    double max_rate_ = 8.0;
    double current_pitch_ = 0.0;
};

class TorqueController {
public:
    TorqueController();
    
    void set_control_type(const std::string& type);
    void set_torque_limits(double min_torque, double max_torque);
    void set_rpm_limits(double min_rpm, double max_rpm);
    
    double compute_torque(double current_rpm, double wind_speed);
    
    void set_kp(double kp) { kp_ = kp; }
    void set_ki(double ki) { ki_ = ki; }

private:
    std::string control_type_ = "quadratic";
    PIDController pid_;
    double kp_ = 50.0;
    double ki_ = 5.0;
    double min_torque_ = 0.0;
    double max_torque_ = 50000.0;
    double min_rpm_ = 700.0;
    double max_rpm_ = 1200.0;
    double rated_rpm_ = 1173.7;
    double rated_torque_ = 41000.0;
};

class YawController {
public:
    YawController();
    
    void set_gains(double kp, double ki);
    void set_rate_limit(double max_rate);
    void set_yaw_error_threshold(double threshold);
    
    double compute_yaw_rate(double yaw_error, double dt);
    
    void set_wind_direction(double direction) { wind_direction_ = direction; }
    double get_wind_direction() const { return wind_direction_; }

private:
    PIDController pid_;
    double max_rate_ = 0.5;
    double yaw_error_threshold_ = 8.0;
    double wind_direction_ = 0.0;
};

}
