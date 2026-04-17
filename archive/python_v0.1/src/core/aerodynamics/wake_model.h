#pragma once

#include <string>
#include <vector>

namespace openturbine {

struct WakePoint {
    double x;      
    double y;      
    double z;      
    double vx;     
    double vy;     
    double vz;     
    double velocity_deficit;
    double turbulence_intensity;
};

class WakeModel {
public:
    WakeModel();
    
    void set_wind_speed(double wind_speed) { wind_speed_ = wind_speed; }
    void set_rotor_diameter(double diameter) { rotor_diameter_ = diameter; }
    void set_thrust_coefficient(double ct) { ct_ = ct; }
    void set_turbulence_intensity(double ti) { turbulence_intensity_ = ti; }
    
    void set_model_type(const std::string& type) { model_type_ = type; }
    
    void calculate_wake_field(double downstream_distance);
    
    std::vector<WakePoint> get_wake_field() const { return wake_field_; }
    double get_velocity_deficit_at(double x, double y, double z) const;
    double get_turbulence_at(double x, double y, double z) const;
    
    double get_wake_expansion_factor(double x) const;
    double get_centerline_velocity_deficit(double x) const;

private:
    double wind_speed_ = 8.0;
    double rotor_diameter_ = 126.0;
    double ct_ = 0.8;
    double turbulence_intensity_ = 0.14;
    
    std::string model_type_ = "jensen";
    
    std::vector<WakePoint> wake_field_;
    
    double jensen_velocity_deficit(double x, double r) const;
    double jensen_wake_width(double x) const;
    double frandsen_velocity_deficit(double x, double r) const;
    double frandsen_wake_width(double x) const;
};

class WakeSolver {
public:
    WakeSolver();
    
    void add_turbine(const std::vector<double>& position,
                     double rotor_diameter,
                     double ct,
                     double turbulence_intensity);
    
    void calculate_wake_interaction();
    
    double get_velocity_at(double x, double y, double z) const;
    std::vector<double> get_velocity_vector(double x, double y, double z) const;
    
    void set_wind_direction(double direction_deg) { wind_direction_ = direction_deg; }
    void set_wind_speed(double speed) { wind_speed_ = speed; }

private:
    double wind_speed_ = 8.0;
    double wind_direction_ = 0.0;
    
    struct Turbine {
        std::vector<double> position;
        double rotor_diameter;
        double ct;
        double turbulence_intensity;
        std::vector<WakePoint> wake_field;
    };
    
    std::vector<Turbine> turbines_;
};

}
