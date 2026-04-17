#include "fatigue.h"
#include <algorithm>
#include <cmath>

namespace openturbine {

FatigueAnalyzer::FatigueAnalyzer() {
}

void FatigueAnalyzer::add_load_range(double range, int cycles) {
    load_ranges_.push_back({range, cycles});
}

void FatigueAnalyzer::calculate_damage() {
    miners_sum_ = 0.0;
    
    if (load_ranges_.empty()) {
        del_ = 0.0;
        fatigue_life_ = 0.0;
        return;
    }
    
    double sum_del_m = 0.0;
    double total_cycles = 0.0;
    
    for (const auto& lr : load_ranges_) {
        double ni = static_cast<double>(lr.cycles);
        double delta_sigma = lr.range;
        
        if (delta_sigma > 0.0) {
            double ni_star = sn_intercept_ / std::pow(delta_sigma, sn_slope_);
            miners_sum_ += ni / ni_star;
            
            sum_del_m += ni * std::pow(delta_sigma, sn_slope_);
            total_cycles += ni;
        }
    }
    
    if (total_cycles > 0.0) {
        del_ = std::pow(sum_del_m / total_cycles, 1.0 / sn_slope_);
    } else {
        del_ = 0.0;
    }
    
    if (del_ > 0.0 && sn_slope_ > 0.0) {
        double n_equivalent = sn_intercept_ / std::pow(del_, sn_slope_);
        double seconds_per_year = 365.25 * 24.0 * 3600.0;
        fatigue_life_ = n_equivalent / (total_cycles / seconds_per_year);
    } else {
        fatigue_life_ = std::numeric_limits<double>::infinity();
    }
}

void FatigueAnalyzer::clear_load_data() {
    load_ranges_.clear();
    miners_sum_ = 0.0;
    del_ = 0.0;
    fatigue_life_ = 0.0;
}

std::vector<int> FatigueAnalyzer::rainflow_counting(const std::vector<double>& stress_history) {
    std::vector<int> rainflow_counts;
    
    return rainflow_counts;
}

}
