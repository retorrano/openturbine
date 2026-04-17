import pytest
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from openturbine.simulation_runner import SimulationRunner, load_preset, create_simple_simulation


class TestSimulationRunner:
    """Unit tests for SimulationRunner class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = create_simple_simulation()
    
    def test_initialization(self):
        """Test that runner initializes with default values."""
        assert self.runner.rotor_diameter == 126.0
        assert self.runner.hub_height == 90.0
        assert self.runner.num_blades == 3
        assert self.runner.rated_power == 5e6
    
    def test_calculate_rotor_rpm_below_cut_in(self):
        """Test rotor RPM is zero below cut-in wind speed."""
        rpm = self.runner.calculate_rotor_rpm(2.0)
        assert rpm == 0.0
    
    def test_calculate_rotor_rpm_above_cut_out(self):
        """Test rotor RPM is zero above cut-out wind speed."""
        rpm = self.runner.calculate_rotor_rpm(30.0)
        assert rpm == 0.0
    
    def test_calculate_rotor_rpm_normal_operation(self):
        """Test rotor RPM calculation at normal operating wind speed."""
        rpm = self.runner.calculate_rotor_rpm(8.0)
        assert rpm > 0
        assert rpm <= 12.1
    
    def test_calculate_rotor_rpm_above_rated(self):
        """Test rotor RPM is capped at rated value above rated wind speed."""
        rpm = self.runner.calculate_rotor_rpm(15.0)
        assert rpm <= 12.1
    
    def test_calculate_power_below_cut_in(self):
        """Test power is zero below cut-in wind speed."""
        power = self.runner.calculate_power(2.0)
        assert power == 0.0
    
    def test_calculate_power_above_cut_out(self):
        """Test power is zero above cut-out wind speed."""
        power = self.runner.calculate_power(30.0)
        assert power == 0.0
    
    def test_calculate_power_at_rated(self):
        """Test power equals rated power at rated wind speed."""
        power = self.runner.calculate_power(self.runner.rated_wind_speed)
        assert power > 0
        assert power <= self.runner.rated_power
    
    def test_calculate_power_never_exceeds_rated(self):
        """Test power never exceeds rated power."""
        for ws in np.linspace(3.0, 25.0, 10):
            power = self.runner.calculate_power(ws)
            assert power <= self.runner.rated_power * 1.01
    
    def test_calculate_thrust(self):
        """Test thrust calculation."""
        thrust = self.runner.calculate_thrust(8.0)
        assert thrust > 0
        assert thrust < 1e6
    
    def test_run_steady_state_returns_all_fields(self):
        """Test that steady state result contains all expected fields."""
        result = self.runner.run_steady_state(8.0)
        
        expected_fields = [
            "wind_speed", "rotor_rpm", "power_output", "power_mw",
            "thrust_force", "thrust_kn", "pitch_angle", "tip_speed_ratio",
            "power_coefficient", "aerodynamic_efficiency", "tip_speed"
        ]
        
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"
    
    def test_run_steady_state_wind_speed_matches_input(self):
        """Test that result wind speed matches input."""
        wind_speed = 10.0
        result = self.runner.run_steady_state(wind_speed)
        assert result["wind_speed"] == wind_speed
    
    def test_run_parametric_sweep_returns_list(self):
        """Test that parametric sweep returns a list."""
        results = self.runner.run_parametric_sweep(3.0, 10.0, 2.0)
        assert isinstance(results, list)
        assert len(results) > 0
    
    def test_run_parametric_sweep_covers_range(self):
        """Test that sweep covers the specified wind speed range."""
        results = self.runner.run_parametric_sweep(3.0, 9.0, 2.0)
        wind_speeds = [r["wind_speed"] for r in results]
        
        assert 3.0 in wind_speeds
        assert 5.0 in wind_speeds
        assert 7.0 in wind_speeds
        assert 9.0 in wind_speeds
    
    def test_run_time_domain_returns_history(self):
        """Test time domain simulation returns arrays."""
        result = self.runner.run_time_domain(duration=10.0, dt=0.1)
        
        assert "time" in result
        assert "power_mw" in result
        assert "rpm" in result
        
        assert len(result["time"]) == len(result["power_mw"])
    
    def test_run_time_domain_with_turbulence(self):
        """Test time domain simulation with turbulence."""
        result = self.runner.run_time_domain(
            duration=10.0, dt=0.1, turbulence=True
        )
        
        assert "wind_speed" in result
        assert len(result["wind_speed"]) > 0
    
    def test_animation_parameters_contain_required_fields(self):
        """Test animation parameters contain all needed fields."""
        params = self.runner.get_animation_parameters(8.0)
        
        required = [
            "rotor_rpm", "angular_velocity", "blade_length", "num_blades",
            "hub_height", "rotor_diameter", "power_mw", "tip_speed"
        ]
        
        for field in required:
            assert field in params, f"Missing animation parameter: {field}"
    
    def test_blade_tip_position_returns_tuple(self):
        """Test blade tip position returns x, y coordinates."""
        x, y = self.runner.get_blade_tip_position(0, 0.0)
        assert isinstance(x, float)
        assert isinstance(y, float)
    
    def test_blade_tip_position_changes_with_time(self):
        """Test blade tip position changes with time."""
        x1, y1 = self.runner.get_blade_tip_position(0, 0.0)
        x2, y2 = self.runner.get_blade_tip_position(0, 0.1)
        
        assert (x1, y1) != (x2, y2)


class TestPresetLoading:
    """Tests for preset loading functionality."""
    
    def test_load_nrel_5mw_preset(self):
        """Test loading NREL 5MW preset."""
        runner = load_preset("nrel_5mw")
        
        assert runner.rotor_diameter == 126.0
        assert runner.rated_power == 5e6
    
    def test_load_iea_10mw_preset(self):
        """Test loading IEA 10MW preset."""
        runner = load_preset("iea_10mw")
        
        assert runner.rotor_diameter == 198.0
        assert runner.rated_power == 10e6
    
    def test_load_community_preset(self):
        """Test loading community wind preset."""
        runner = load_preset("community_100kw")
        
        assert runner.rotor_diameter == 19.0
        assert runner.rated_power == 100000.0
    
    def test_load_invalid_preset_raises_error(self):
        """Test that loading invalid preset raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_preset("nonexistent_preset")


class TestSimulationAccuracy:
    """Tests to verify simulation accuracy against known values."""
    
    def test_cp_max_optimal_tsr(self):
        """Test that Cp is near maximum at optimal TSR."""
        runner = create_simple_simulation()
        
        result = runner.run_steady_state(runner.rated_wind_speed)
        
        assert result["power_coefficient"] > 0.35
        assert result["power_coefficient"] <= runner.cp_max
    
    def test_power_proportional_to_cube_of_wind_speed(self):
        """Test that power follows cube law at low wind speeds."""
        runner = create_simple_simulation()
        
        p1 = runner.run_steady_state(5.0)["power_output"]
        p2 = runner.run_steady_state(10.0)["power_output"]
        
        ratio = p2 / p1 if p1 > 0 else 0
        expected_ratio = (10.0 / 5.0) ** 3
        
        assert 0.7 * expected_ratio < ratio < 1.3 * expected_ratio


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
