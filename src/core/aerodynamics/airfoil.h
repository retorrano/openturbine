#pragma once

#include <vector>
#include <string>
#include "bem_solver.h"

namespace openturbine {

class Airfoil {
public:
    Airfoil();
    explicit Airfoil(const std::string& name);
    
    void set_name(const std::string& name) { name_ = name; }
    std::string get_name() const { return name_; }
    
    void add_polar_point(double alpha, double cl, double cd, double cm = 0.0);
    void set_thickness(double thickness) { thickness_ = thickness; }
    void set_camber(double camber) { camber_ = camber; }
    
    double get_cl(double alpha) const;
    double get_cd(double alpha) const;
    double get_cm(double alpha) const;
    double get_cl_max() const { return cl_max_; }
    double get_cd_min() const { return cd_min_; }
    double get_stall_angle() const { return alpha_stall_; }
    
    void generate_naca_4digit(int naca_number, int num_points = 100);
    void generate_flat_plate(double thickness, int num_points = 50);
    
    std::vector<double> get_alpha() const { return alpha_; }
    std::vector<double> get_cl() const { return cl_; }
    std::vector<double> get_cd() const { return cd_; }
    std::vector<double> get_cm() const { return cm_; }
    
private:
    std::string name_;
    std::vector<double> alpha_;
    std::vector<double> cl_;
    std::vector<double> cd_;
    std::vector<double> cm_;
    double thickness_ = 0.0;
    double camber_ = 0.0;
    double cl_max_ = 0.0;
    double cd_min_ = 1e10;
    double alpha_stall_ = 0.0;
    
    double interpolate(const std::vector<double>& x, 
                      const std::vector<double>& y, 
                      double xi) const;
};

class AirfoilDatabase {
public:
    static AirfoilDatabase& get_instance();
    
    void add_airfoil(const Airfoil& airfoil);
    Airfoil get_airfoil(const std::string& name) const;
    bool has_airfoil(const std::string& name) const;
    
    void load_default_airfoils();
    void load_from_file(const std::string& filename);
    
    std::vector<std::string> get_available_airfoils() const;

private:
    AirfoilDatabase();
    AirfoilDatabase(const AirfoilDatabase&) = delete;
    AirfoilDatabase& operator=(const AirfoilDatabase&) = delete;
    
    std::vector<Airfoil> airfoils_;
};

}
