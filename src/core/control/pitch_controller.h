#pragma once

#include <vector>

namespace openturbine {

class CollectivePitchController {
public:
    CollectivePitchController();
    
    void set_parameters(double kp, double ki, double kd,
                        double min_pitch, double max_pitch,
                        double min_rate, double max_rate);
    
    double compute(double rated_rpm, double current_rpm, double dt);
    double compute_with_wind(double rated_rpm, double current_rpm, 
                             double wind_speed, double rated_wind, double dt);
    
    void reset();
    void set_current_pitch(double pitch) { current_pitch_ = pitch; }
    double get_current_pitch() const { return current_pitch_; }

private:
    double kp_ = 0.018;
    double ki_ = 0.002;
    double kd_ = 0.0;
    double min_pitch_ = 0.0;
    double max_pitch_ = 90.0;
    double min_rate_ = -8.0;
    double max_rate_ = 8.0;
    
    double current_pitch_ = 0.0;
    double integral_ = 0.0;
    double last_error_ = 0.0;
    bool first_call_ = true;
};

class IndividualPitchController {
public:
    IndividualPitchController();
    
    void set_collective_controller(CollectivePitchController& controller) { pitch_controller_ = controller; }
    void set_number_of_blades(int num) { num_blades_ = num; }
    void set_tilt_angle(double angle) { tilt_angle_ = angle; }
    void set_yaw_misalignment(double angle) { yaw_misalignment_ = angle; }
    
    std::vector<double> compute(const std::vector<double>& blade_loads,
                                 double wind_direction,
                                 double dt);
    
    std::vector<double> get_individual_pitch() const { return individual_pitch_; }

private:
    int num_blades_ = 3;
    double tilt_angle_ = 0.0;
    double yaw_misalignment_ = 0.0;
    CollectivePitchController pitch_controller_;
    std::vector<double> individual_pitch_;
};

}
