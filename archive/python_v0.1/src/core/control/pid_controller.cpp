#include "pid_controller.h"
#include <algorithm>

namespace openturbine {

PIDController::PIDController()
    : kp_(0.0), ki_(0.0), kd_(0.0)
{
}

PIDController::PIDController(double kp, double ki, double kd)
    : kp_(kp), ki_(ki), kd_(kd)
{
}

void PIDController::set_gains(double kp, double ki, double kd) {
    kp_ = kp;
    ki_ = ki;
    kd_ = kd;
}

void PIDController::set_output_limits(double min_out, double max_out) {
    min_output_ = min_out;
    max_output_ = max_out;
}

void PIDController::set_integral_limit(double limit) {
    integral_limit_ = std::abs(limit);
}

void PIDController::set_derivative_filter(double filter_coeff) {
    derivative_filter_ = std::abs(filter_coeff);
}

double PIDController::compute(double setpoint, double measurement, double dt) {
    double error = setpoint - measurement;
    
    integral_ += error * dt;
    integral_ = std::max(-integral_limit_, std::min(integral_limit_, integral_));
    
    double derivative = 0.0;
    if (!first_step_ && dt > 0.0) {
        derivative = (error - last_error_) / dt;
        
        if (derivative_filter_ > 0.0) {
            double alpha = derivative_filter_ * dt;
            derivative = alpha * derivative + (1.0 - alpha) * derivative;
        }
    }
    
    double output = kp_ * error + ki_ * integral_ + kd_ * derivative;
    output = std::max(min_output_, std::min(max_output_, output));
    
    last_error_ = error;
    last_output_ = output;
    first_step_ = false;
    
    return output;
}

void PIDController::reset() {
    integral_ = 0.0;
    last_error_ = 0.0;
    last_measurement_ = 0.0;
    last_output_ = 0.0;
    first_step_ = true;
}

PitchController::PitchController()
{
}

PitchController::PitchController(double kp, double ki, double kd)
    : pid_(kp, ki, kd)
{
}

void PitchController::set_gains(double kp, double ki, double kd) {
    pid_.set_gains(kp, ki, kd);
}

void PitchController::set_pitch_limits(double min_pitch, double max_pitch) {
    min_pitch_ = min_pitch;
    max_pitch_ = max_pitch;
}

void PitchController::set_rate_limits(double min_rate, double max_rate) {
    min_rate_ = min_rate;
    max_rate_ = max_rate;
}

double PitchController::compute_pitch(double rated_rpm, double current_rpm, double dt) {
    double pitch_command = pid_.compute(rated_rpm, current_rpm, dt);
    
    pitch_command = std::max(min_pitch_, std::min(max_pitch_, pitch_command));
    
    double rate = pitch_command - current_pitch_;
    if (dt > 0.0) {
        rate = rate / dt;
        rate = std::max(min_rate_, std::min(max_rate_, rate));
        pitch_command = current_pitch_ + rate * dt;
    }
    
    pitch_command = std::max(min_pitch_, std::min(max_pitch_, pitch_command));
    
    current_pitch_ = pitch_command;
    return pitch_command;
}

TorqueController::TorqueController()
{
}

void TorqueController::set_control_type(const std::string& type) {
    control_type_ = type;
}

void TorqueController::set_torque_limits(double min_torque, double max_torque) {
    min_torque_ = min_torque;
    max_torque_ = max_torque;
}

void TorqueController::set_rpm_limits(double min_rpm, double max_rpm) {
    min_rpm_ = min_rpm;
    max_rpm_ = max_rpm;
}

double TorqueController::compute_torque(double current_rpm, double wind_speed) {
    double torque = 0.0;
    
    if (control_type_ == "constant") {
        torque = rated_torque_;
    }
    else if (control_type_ == "linear") {
        if (current_rpm < min_rpm_) {
            torque = min_torque_;
        } else if (current_rpm < rated_rpm_) {
            double k = (rated_torque_ - min_torque_) / (rated_rpm_ - min_rpm_);
            torque = min_torque_ + k * (current_rpm - min_rpm_);
        } else {
            torque = rated_torque_;
        }
    }
    else if (control_type_ == "quadratic") {
        if (current_rpm < min_rpm_) {
            torque = min_torque_;
        } else if (current_rpm < rated_rpm_) {
            double k = rated_torque_ / (rated_rpm_ * rated_rpm_);
            torque = k * current_rpm * current_rpm;
        } else {
            torque = rated_torque_;
        }
    }
    
    torque = std::max(min_torque_, std::min(max_torque_, torque));
    return torque;
}

YawController::YawController()
{
}

void YawController::set_gains(double kp, double ki) {
    pid_.set_gains(kp, ki, 0.0);
}

void YawController::set_rate_limit(double max_rate) {
    max_rate_ = max_rate;
}

void YawController::set_yaw_error_threshold(double threshold) {
    yaw_error_threshold_ = threshold;
}

double YawController::compute_yaw_rate(double yaw_error, double dt) {
    if (std::abs(yaw_error) < yaw_error_threshold_) {
        return 0.0;
    }
    
    double rate = pid_.compute(0.0, yaw_error, dt);
    rate = std::max(-max_rate_, std::min(max_rate_, rate));
    
    return rate;
}

}
