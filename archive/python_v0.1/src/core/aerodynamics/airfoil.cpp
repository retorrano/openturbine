#include "airfoil.h"
#include <algorithm>
#include <cmath>
#include <fstream>
#include <sstream>

namespace openturbine {

Airfoil::Airfoil() : name_("default") {
}

Airfoil::Airfoil(const std::string& name) : name_(name) {
}

void Airfoil::add_polar_point(double alpha_deg, double cl, double cd, double cm) {
    alpha_.push_back(alpha_deg);
    cl_.push_back(cl);
    cd_.push_back(cd);
    cm_.push_back(cm);
    
    if (cl > cl_max_) {
        cl_max_ = cl;
        alpha_stall_ = alpha_deg;
    }
    if (cd < cd_min_) {
        cd_min_ = cd;
    }
}

double Airfoil::get_cl(double alpha_deg) const {
    if (alpha_.empty()) {
        return 2.0 * M_PI * alpha_deg * M_PI / 180.0;
    }
    return interpolate(alpha_, cl_, alpha_deg);
}

double Airfoil::get_cd(double alpha_deg) const {
    if (cd_.empty()) {
        return 0.008;
    }
    return interpolate(alpha_, cd_, alpha_deg);
}

double Airfoil::get_cm(double alpha_deg) const {
    if (cm_.empty()) {
        return 0.0;
    }
    return interpolate(alpha_, cm_, alpha_deg);
}

double Airfoil::interpolate(const std::vector<double>& x,
                             const std::vector<double>& y,
                             double xi) const {
    if (x.size() != y.size() || x.empty()) {
        return 0.0;
    }
    
    if (xi <= x.front()) {
        return y.front();
    }
    if (xi >= x.back()) {
        return y.back();
    }
    
    for (size_t i = 0; i < x.size() - 1; ++i) {
        if (xi >= x[i] && xi <= x[i + 1]) {
            double t = (xi - x[i]) / (x[i + 1] - x[i]);
            return y[i] + t * (y[i + 1] - y[i]);
        }
    }
    
    return 0.0;
}

void Airfoil::generate_naca_4digit(int naca_number, int num_points) {
    name_ = "NACA " + std::to_string(naca_number);
    
    int m = naca_number / 1000;
    int p = (naca_number / 100) % 10;
    int t = naca_number % 100;
    
    thickness_ = t / 100.0;
    camber_ = m / 100.0;
    
    double max_camber_pos = p / 10.0;
    
    for (int i = 0; i <= num_points; ++i) {
        double x = static_cast<double>(i) / num_points;
        
        double yt = 5.0 * thickness_ * (
            0.2969 * std::sqrt(x) 
            - 0.1260 * x 
            - 0.3516 * x * x 
            + 0.2843 * x * x * x 
            - 0.1015 * x * x * x * x
        );
        
        double yc, dyc;
        if (x <= max_camber_pos) {
            yc = (m / (p * p)) * (2.0 * p * x - x * x);
            dyc = (2.0 * m / (p * p)) * (p - x);
        } else {
            yc = (m / ((1.0 - p) * (1.0 - p))) * 
                 (1.0 - 2.0 * p + 2.0 * p * x - x * x);
            dyc = (2.0 * m / ((1.0 - p) * (1.0 - p))) * (p - x);
        }
        
        double theta = std::atan(dyc);
        
        double alpha_deg = -theta * 180.0 / M_PI;
        double cl = 2.0 * M_PI * theta;
        double cd = 0.0;
        
        if (x > 0.0) {
            cd = 0.0095 / (cl * cl + 0.01) + 0.01 * thickness_;
        }
        
        add_polar_point(alpha_deg, cl, cd, 0.0);
    }
}

void Airfoil::generate_flat_plate(double thickness, int num_points) {
    name_ = "Flat Plate t=" + std::to_string(thickness);
    thickness_ = thickness;
    camber_ = 0.0;
    
    for (int i = 0; i <= num_points; ++i) {
        double alpha = -180.0 + 360.0 * i / num_points;
        double cl = 2.0 * M_PI * alpha * M_PI / 180.0;
        double cd = 0.0;
        
        if (alpha < -90.0 || alpha > 90.0) {
            cl = 0.0;
            cd = 2.0;
        } else if (std::abs(alpha) > 15.0) {
            cl = 0.9 * 2.0 * M_PI * std::sin(alpha * M_PI / 180.0);
            cd = 0.02 + 0.001 * std::abs(alpha - 15.0);
        }
        
        add_polar_point(alpha, cl, cd, 0.0);
    }
}

AirfoilDatabase& AirfoilDatabase::get_instance() {
    static AirfoilDatabase instance;
    return instance;
}

AirfoilDatabase::AirfoilDatabase() {
    load_default_airfoils();
}

void AirfoilDatabase::add_airfoil(const Airfoil& airfoil) {
    airfoils_.push_back(airfoil);
}

Airfoil AirfoilDatabase::get_airfoil(const std::string& name) const {
    for (const auto& af : airfoils_) {
        if (af.get_name() == name) {
            return af;
        }
    }
    return Airfoil();
}

bool AirfoilDatabase::has_airfoil(const std::string& name) const {
    for (const auto& af : airfoils_) {
        if (af.get_name() == name) {
            return true;
        }
    }
    return false;
}

void AirfoilDatabase::load_default_airfoils() {
    Airfoil cylinder;
    cylinder.set_name("cylinder");
    cylinder.generate_flat_plate(1.0, 72);
    airfoils_.push_back(cylinder);
    
    Airfoil naca0012;
    naca0012.generate_naca_4digit(12, 100);
    airfoils_.push_back(naca0012);
    
    Airfoil naca4412;
    naca4412.generate_naca_4digit(4412, 100);
    airfoils_.push_back(naca4412);
    
    Airfoil naca63418;
    naca63418.generate_naca_4digit(63418, 100);
    airfoils_.push_back(naca63418);
}

void AirfoilDatabase::load_from_file(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        return;
    }
    
    Airfoil airfoil;
    std::string line;
    
    while (std::getline(file, line)) {
        if (line.empty() || line[0] == '#') {
            continue;
        }
        
        std::istringstream iss(line);
        double alpha, cl, cd, cm;
        if (iss >> alpha >> cl >> cd >> cm) {
            airfoil.add_polar_point(alpha, cl, cd, cm);
        }
    }
    
    if (!airfoil.get_alpha().empty()) {
        airfoils_.push_back(airfoil);
    }
}

std::vector<std::string> AirfoilDatabase::get_available_airfoils() const {
    std::vector<std::string> names;
    for (const auto& af : airfoils_) {
        names.push_back(af.get_name());
    }
    return names;
}

}
