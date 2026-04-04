import pytest
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from openturbine.simulation_runner import SimulationRunner, load_preset
from openturbine.models.turbine_config import ProjectConfig
from openturbine.models.simulation_result import SimulationResult, ParametricSweepResult


class TestEndToEndSimulation:
    """End-to-end integration tests for simulation workflow."""
    
    def test_full_simulation_workflow(self):
        """Test complete simulation workflow from config to results."""
        runner = SimulationRunner()
        
        steady_state = runner.run_steady_state(8.0)
        
        assert steady_state["wind_speed"] == 8.0
        assert steady_state["power_output"] > 0
        
        sweep_results = runner.run_parametric_sweep(3.0, 15.0, 3.0)
        
        assert len(sweep_results) > 0
        
        time_domain = runner.run_time_domain(10.0, 0.1)
        
        assert "time" in time_domain
        assert len(time_domain["time"]) == 100
    
    def test_preset_to_simulation_workflow(self):
        """Test loading preset and running simulation."""
        runner = load_preset("nrel_5mw")
        
        result = runner.run_steady_state(11.4)
        
        assert result["power_mw"] > 4.0
    
    def test_config_save_load_simulation(self, tmp_path):
        """Test saving config, running simulation, and saving results."""
        config = ProjectConfig()
        config.name = "Test Simulation"
        
        config_path = tmp_path / "config.json"
        config.save(str(config_path))
        
        loaded_config = ProjectConfig.from_file(str(config_path))
        assert loaded_config.name == "Test Simulation"
        
        runner = SimulationRunner(loaded_config.turbine.to_dict())
        result_dict = runner.run_steady_state(8.0)
        
        result = SimulationResult(
            wind_speed=result_dict["wind_speed"],
            power_output=result_dict["power_output"],
            rotor_rpm=result_dict["rotor_rpm"],
            thrust_force=result_dict["thrust_force"]
        )
        
        result_path = tmp_path / "result.json"
        result.save(str(result_path))
        
        loaded_result = SimulationResult.load(str(result_path))
        assert loaded_result.wind_speed == result_dict["wind_speed"]
    
    def test_parametric_sweep_to_annual_energy(self):
        """Test running parametric sweep and calculating annual energy."""
        runner = SimulationRunner()
        
        sweep = runner.run_parametric_sweep(3.0, 15.0, 2.0)
        
        sweep_result = ParametricSweepResult()
        for r in sweep:
            result = SimulationResult(
                wind_speed=r["wind_speed"],
                power_output=r["power_output"]
            )
            sweep_result.add_result(result)
        
        annual_energy = sweep_result.get_annual_energy_mwh()
        
        assert annual_energy > 0
    
    def test_capacity_factor_calculation(self):
        """Test capacity factor calculation."""
        runner = SimulationRunner()
        
        cf = runner.calculate_capacity_factor(8.0)
        
        assert 0.0 <= cf <= 1.0
    
    def test_animation_parameters_consistency(self):
        """Test that animation parameters are consistent with simulation."""
        runner = SimulationRunner()
        
        wind_speed = 8.0
        sim_result = runner.run_steady_state(wind_speed)
        anim_params = runner.get_animation_parameters(wind_speed)
        
        assert abs(sim_result["rotor_rpm"] - anim_params["rotor_rpm"]) < 0.01


class TestMultiConfiguration:
    """Tests across multiple turbine configurations."""
    
    def test_all_presets_simulate(self):
        """Test that all presets can run simulations."""
        presets = ["nrel_5mw", "iea_10mw", "community_100kw"]
        
        for preset_name in presets:
            runner = load_preset(preset_name)
            result = runner.run_steady_state(8.0)
            
            assert result["power_output"] >= 0
            assert result["rotor_rpm"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
