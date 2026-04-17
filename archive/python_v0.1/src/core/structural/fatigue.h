#pragma once

#include <vector>

namespace openturbine {

class FatigueAnalyzer {
public:
    FatigueAnalyzer();
    
    void set_sn_curve_slope(double m) { sn_slope_ = m; }
    void set_sn_curve_intercept(double a) { sn_intercept_ = a; }
    void set_target_miners_sum(double target) { target_miners_sum_ = target; }
    
    void add_load_range(double range, int cycles);
    
    void calculate_damage();
    
    double get_miners_sum() const { return miners_sum_; }
    double get_damage_equivalent_load() const { return del_; }
    double get_fatigue_life_years() const { return fatigue_life_; }
    bool is_fatigue_valid() const { return miners_sum_ < target_miners_sum_; }
    
    void clear_load_data();

private:
    double sn_slope_ = 10.0;
    double sn_intercept_ = 1e8;
    double target_miners_sum_ = 1.0;
    
    struct LoadRangeData {
        double range;
        int cycles;
    };
    std::vector<LoadRangeData> load_ranges_;
    
    double miners_sum_ = 0.0;
    double del_ = 0.0;
    double fatigue_life_ = 0.0;
    
    std::vector<int> rainflow_counting(const std::vector<double>& stress_history);
};

}
