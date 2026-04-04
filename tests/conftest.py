import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_turbine_config():
    """Provide a sample turbine configuration for tests."""
    return {
        "rotor": {
            "diameter": {"value": 126.0, "unit": "m"},
            "hub_height": {"value": 90.0, "unit": "m"},
            "number_of_blades": {"value": 3},
            "rated_power": {"value": 5e6, "unit": "W"}
        },
        "tower": {
            "height": {"value": 90.0, "unit": "m"}
        }
    }


@pytest.fixture
def sample_wind_speeds():
    """Provide sample wind speeds for tests."""
    return [3.0, 5.0, 8.0, 11.4, 15.0, 20.0, 25.0]
