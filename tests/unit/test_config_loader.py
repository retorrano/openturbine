import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from openturbine.utils.config_loader import (
    load_config, load_all_configs, merge_configs,
    validate_config, get_parameter_value, set_parameter_value
)


class TestConfigLoader:
    """Tests for configuration loader utility."""
    
    def test_load_turbine_config(self):
        """Test loading turbine configuration."""
        config = load_config("turbine")
        
        assert isinstance(config, dict)
        assert "rotor" in config or "version" in config
    
    def test_load_aerodynamics_config(self):
        """Test loading aerodynamics configuration."""
        config = load_config("aerodynamics")
        
        assert isinstance(config, dict)
    
    def test_load_all_configs(self):
        """Test loading all configurations."""
        configs = load_all_configs()
        
        expected = ["turbine", "aerodynamics", "structural", "control", "environment", "simulation"]
        
        for key in expected:
            assert key in configs
    
    def test_validate_config_valid(self):
        """Test validation of valid config."""
        config = {
            "version": "1.0",
            "name": "Test Config"
        }
        
        assert validate_config(config) is True
    
    def test_validate_config_missing_version(self):
        """Test validation fails for missing version."""
        config = {
            "name": "Test Config"
        }
        
        assert validate_config(config) is False
    
    def test_validate_config_missing_name(self):
        """Test validation fails for missing name."""
        config = {
            "version": "1.0"
        }
        
        assert validate_config(config) is False


class TestConfigMerge:
    """Tests for configuration merging."""
    
    def test_merge_configs_override_value(self):
        """Test merging where override changes a value."""
        base = {"a": 1, "b": 2}
        override = {"b": 3}
        
        result = merge_configs(base, override)
        
        assert result["a"] == 1
        assert result["b"] == 3
    
    def test_merge_configs_adds_new_key(self):
        """Test merging where override adds a new key."""
        base = {"a": 1}
        override = {"b": 2}
        
        result = merge_configs(base, override)
        
        assert "b" in result
        assert result["b"] == 2
    
    def test_merge_configs_nested(self):
        """Test merging with nested dictionaries."""
        base = {"outer": {"inner": 1, "keep": 2}}
        override = {"outer": {"inner": 10}}
        
        result = merge_configs(base, override)
        
        assert result["outer"]["inner"] == 10
        assert result["outer"]["keep"] == 2


class TestParameterAccess:
    """Tests for parameter get/set functions."""
    
    def test_get_parameter_value_simple(self):
        """Test getting simple parameter value."""
        params = {"a": {"value": 1}}
        
        assert get_parameter_value(params, "a") == 1
    
    def test_get_parameter_value_nested(self):
        """Test getting nested parameter value."""
        params = {"outer": {"inner": {"value": 42}}}
        
        assert get_parameter_value(params, "outer.inner") == 42
    
    def test_get_parameter_value_default(self):
        """Test getting parameter with default for missing key."""
        params = {"a": 1}
        
        result = get_parameter_value(params, "nonexistent", default=99)
        
        assert result == 99
    
    def test_set_parameter_value(self):
        """Test setting parameter value."""
        params = {"a": {"value": 1}}
        
        set_parameter_value(params, "a", 10)
        
        assert params["a"]["value"] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
