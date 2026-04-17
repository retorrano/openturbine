#pragma once

#include <string>
#include <vector>
#include <cmath>

namespace openturbine {

struct AirfoilData {
    std::string name;
    std::vector<double> alpha;      
    std::vector<double> cl;         
    std::vector<double> cd;         
    std::vector<double> cm;         
    double thickness = 0.0;
    double camber = 0.0;
};

class BEMSolver {
public:
    BEMSolver();
    
    void set_rotor_radius(double radius);
    void set_num_blades(int num_blades);
    void set_blade_data(const std::vector<double>& chord, 
                        const std::vector<double>& twist,
                        const std::vector<double>& position);
    void set_airfoil_data(const AirfoilData& airfoil);
    
    void set_wind_speed(double wind_speed);
    void set_tip_speed_ratio(double tsr);
    void set_pitch_angle(double pitch);
    void set_air_density(double rho);
    
    void set_use_tip_loss(bool use) { use_tip_loss_ = use; }
    void set_use_hub_loss(bool use) { use_hub_loss_ = use; }
    void set_use_glauert_correction(bool use) { use_glauert_correction_ = use; }
    
    void solve();
    
    double get_thrust_coefficient() const { return ct_; }
    double get_power_coefficient() const { return cp_; }
    double get_induction_factor() const { return a_; }
    double get_averaged_angle_of_attack() const { return alpha_avg_; }
    
    std::vector<double> get_local_thrust() const { return local_thrust_; }
    std::vector<double> get_local_power() const { return local_power_; }
    std::vector<double> get_local_angle_of_attack() const { return local_alpha_; }
    std::vector<double> get_local_induction() const { return local_a_; }
    
private:
    double rotor_radius_ = 63.0;
    int num_blades_ = 3;
    int num_stations_ = 20;
    
    std::vector<double> chord_;      
    std::vector<double> twist_;      
    std::vector<double> station_;    
    
    AirfoilData airfoil_;
    
    double wind_speed_ = 8.0;
    double tip_speed_ratio_ = 7.55;
    double pitch_angle_ = 0.0;
    double air_density_ = 1.225;
    
    bool use_tip_loss_ = true;
    bool use_hub_loss_ = true;
    bool use_glauert_correction_ = true;
    
    double ct_ = 0.0;
    double cp_ = 0.0;
    double a_ = 0.0;
    double alpha_avg_ = 0.0;
    
    std::vector<double> local_thrust_;
    std::vector<double> local_power_;
    std::vector<double> local_alpha_;
    std::vector<double> local_a_;
    
    double interpolate_cl(double alpha);
    double interpolate_cd(double alpha);
    double calculate_prandtl_tip_loss(double r);
    double calculate_prandtl_hub_loss(double r);
    double solve_single_station(double r, int iteration);
};

}
