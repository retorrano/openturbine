import pytest
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from openturbine.models.turbine_config import (
    TurbineConfig, RotorConfig, TowerConfig, ProjectConfig
)
from openturbine.models.simulation_result import (
    SimulationResult, ParametricSweepResult
)


class TestTurbineConfig:
    """Tests for TurbineConfig model."""
    
    def test_default_rotor_config(self):
        """Test default rotor configuration."""
        rotor = RotorConfig()
        
        assert rotor.diameter == 126.0
        assert rotor.hub_height == 90.0
        assert rotor.number_of_blades == 3
        assert rotor.rated_power == 5_000_000.0
    
    def test_rotor_config_custom_values(self):
        """Test rotor configuration with custom values."""
        rotor = RotorConfig(
            diameter=100.0,
            number_of_blades=2,
            rated_power=2_000_000.0
        )
        
        assert rotor.diameter == 100.0
        assert rotor.number_of_blades == 2
        assert rotor.rated_power == 2_000_000.0
    
    def test_turbine_config_to_dict(self):
        """Test converting turbine config to dictionary."""
        config = TurbineConfig()
        data = config.to_dict()
        
        assert "rotor" in data
        assert "tower" in data
        assert "nacelle" in data
        assert "hub" in data
    
    def test_turbine_config_from_dict(self):
        """Test creating turbine config from dictionary."""
        data = {
            "rotor": {"diameter": 150.0, "hub_height": 100.0, "number_of_blades": 3},
            "tower": {},
            "nacelle": {},
            "hub": {}
        }
        
        config = TurbineConfig.from_dict(data)
        
        assert config.rotor.diameter == 150.0
        assert config.rotor.hub_height == 100.0


class TestSimulationResult:
    """Tests for SimulationResult model."""
    
    def test_default_simulation_result(self):
        """Test default simulation result."""
        result = SimulationResult()
        
        assert result.wind_speed == 0.0
        assert result.rotor_rpm == 0.0
        assert result.power_output == 0.0
    
    def test_simulation_result_with_values(self):
        """Test simulation result with actual values."""
        result = SimulationResult(
            wind_speed=8.0,
            rotor_rpm=12.0,
            power_output=5_000_000.0,
            thrust_force=500_000.0
        )
        
        assert result.wind_speed == 8.0
        assert result.rotor_rpm == 12.0
        assert result.power_output == 5_000_000.0
    
    def test_get_power_mw(self):
        """Test power conversion to MW."""
        result = SimulationResult(power_output=5_000_000.0)
        
        assert result.get_power_mw() == 5.0
    
    def test_get_thrust_kn(self):
        """Test thrust conversion to kN."""
        result = SimulationResult(thrust_force=500_000.0)
        
        assert result.get_thrust_kn() == 500.0
    
    def test_simulation_result_save_load(self, tmp_path):
        """Test saving and loading simulation results."""
        result = SimulationResult(
            wind_speed=10.0,
            power_output=4_000_000.0
        )
        
        filepath = tmp_path / "result.json"
        result.save(str(filepath))
        
        loaded = SimulationResult.load(str(filepath))
        
        assert loaded.wind_speed == result.wind_speed
        assert loaded.power_output == result.power_output


class TestParametricSweepResult:
    """Tests for ParametricSweepResult model."""
    
    def test_add_result(self):
        """Test adding results to sweep."""
        sweep = ParametricSweepResult()
        
        result1 = SimulationResult(wind_speed=5.0, power_output=1_000_000.0)
        result2 = SimulationResult(wind_speed=10.0, power_output=4_000_000.0)
        
        sweep.add_result(result1)
        sweep.add_result(result2)
        
        assert len(sweep.results) == 2
        assert len(sweep.wind_speeds) == 2
        assert len(sweep.power_curve) == 2
    
    def test_get_annual_energy(self):
        """Test annual energy calculation."""
        sweep = ParametricSweepResult()
        
        for ws in [5.0, 8.0, 10.0, 12.0]:
            result = SimulationResult(
                wind_speed=ws,
                power_output=5_000_000.0
            )
            sweep.add_result(result)
        
        energy = sweep.get_annual_energy_mwh()
        
        assert energy > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
