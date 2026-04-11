import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import math
import json
from pathlib import Path


class SimulationRunner:
    """Python interface for running wind turbine simulations."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.results = None
        self._parse_config()

    def _get_default_config(self) -> Dict[str, Any]:
        base_dir = Path(__file__).parent.parent.parent.parent / "configs" / "defaults"

        configs = {}
        for json_file in base_dir.glob("*.json"):
            with open(json_file) as f:
                configs[json_file.stem] = json.load(f)

        return configs

    def _parse_config(self):
        turbine = self.config.get("turbine", {})
        aero = self.config.get("aerodynamics", {})
        control = self.config.get("control", {})
        env = self.config.get("environment", {})

        self.rotor_diameter = self._get_nested_value(turbine, "rotor.diameter.value", 126.0)
        self.hub_height = self._get_nested_value(turbine, "hub_height.value", 90.0)
        self.num_blades = self._get_nested_value(turbine, "rotor.number_of_blades.value", 3)
        self.rated_power = self._get_nested_value(turbine, "rotor.rated_power.value", 5e6)

        self.blade_length = self._get_nested_value(aero, "blade_length.value", 61.5)
        self.cut_in_wind_speed = self._get_nested_value(aero, "cut_in_wind_speed.value", 3.0)
        self.rated_wind_speed = self._get_nested_value(aero, "rated_wind_speed.value", 11.4)
        self.cut_out_wind_speed = self._get_nested_value(aero, "cut_out_wind_speed.value", 25.0)
        self.cp_max = self._get_nested_value(aero, "cp_max.value", 0.42)
        self.tsr_optimal = self._get_nested_value(aero, "tsr_optimal.value", 7.55)

        self.air_density = self._get_nested_value(env, "air_density.value", 1.225)
        self.turbulence_intensity = self._get_nested_value(env, "turbulence_intensity.value", 0.14)

    def _get_nested_value(self, config: Dict, path: str, default: Any) -> Any:
        keys = path.split(".")
        value = config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key, default)
            else:
                return default
        if isinstance(value, dict):
            return value.get("value", default)
        return value

    def calculate_rotor_rpm(self, wind_speed: float, pitch_angle: float = 0.0) -> float:
        """Calculate rotor RPM based on wind speed."""
        if wind_speed < self.cut_in_wind_speed or wind_speed > self.cut_out_wind_speed:
            return 0.0

        tsr = self.tsr_optimal
        if wind_speed > self.rated_wind_speed:
            tsr = self.tsr_optimal * (self.rated_wind_speed / wind_speed)

        tip_speed = wind_speed * tsr
        rotor_radius = self.rotor_diameter / 2.0
        rpm = (tip_speed / (2 * math.pi * rotor_radius)) * 60.0

        return float(min(rpm, 12.1))

    def calculate_power(
        self, wind_speed: float, pitch_angle: float = 0.0, rotor_rpm: Optional[float] = None
    ) -> float:
        """Calculate power output in Watts."""
        if wind_speed < self.cut_in_wind_speed or wind_speed > self.cut_out_wind_speed:
            return 0.0

        if rotor_rpm is None:
            rotor_rpm = self.calculate_rotor_rpm(wind_speed, pitch_angle)

        blade_radius = self.blade_length
        swept_area = math.pi * blade_radius**2

        tsr = (rotor_rpm * 2 * math.pi / 60.0) * blade_radius / wind_speed if wind_speed > 0 else 0

        cp = self._calculate_cp(tsr, pitch_angle)

        power = 0.5 * self.air_density * swept_area * cp * wind_speed**3

        return float(min(power, self.rated_power))

    def _calculate_cp(self, tsr: float, pitch_angle: float) -> float:
        """Calculate power coefficient based on tip speed ratio and pitch.

        Uses a proper Cp-TSR curve that varies with TSR and respects cp_max.
        More blades = higher solidity = lower optimal TSR = lower peak Cp.
        Betz limit ~0.59, practical turbines: 2-blade ~0.47, 3-blade ~0.42, 4-blade ~0.38.
        """
        if tsr <= 0 or tsr > 15:
            return 0.0

        peak_cp = self.cp_max - 0.04 * (self.num_blades - 3)
        peak_cp = max(0.1, min(peak_cp, 0.59))

        optimal_tsr = self.tsr_optimal

        adjusted_optimal_tsr = optimal_tsr * (1.0 + 0.08 * (self.num_blades - 3))

        if pitch_angle < 0.1:
            tsr_deviation = (tsr - adjusted_optimal_tsr) / adjusted_optimal_tsr
            cp_curve = peak_cp * (1.0 - tsr_deviation**2)
        else:
            pitch_rad = math.radians(pitch_angle)
            pitch_factor = 1.0 - 0.4 * pitch_rad - 0.002 * pitch_rad**2
            pitch_factor = max(0.0, min(pitch_factor, 1.0))
            tsr_deviation = (tsr - adjusted_optimal_tsr) / adjusted_optimal_tsr
            cp_curve = peak_cp * pitch_factor * (1.0 - tsr_deviation**2)

        cp = max(0.0, min(cp_curve, peak_cp))

        return float(cp)

    def calculate_thrust(self, wind_speed: float, pitch_angle: float = 0.0) -> float:
        """Calculate thrust force in Newtons.

        More blades = higher solidity = larger projected area = higher thrust.
        """
        if wind_speed < self.cut_in_wind_speed or wind_speed > self.cut_out_wind_speed:
            return 0.0

        rotor_radius = self.rotor_diameter / 2.0
        swept_area = math.pi * rotor_radius**2

        ct = 0.8 * (1.0 - 0.09 * self.tsr_optimal)
        ct = ct * (1.0 + 0.15 * (self.num_blades - 3))
        ct = max(0.0, min(ct, 1.0))

        thrust = 0.5 * self.air_density * swept_area * ct * wind_speed**2

        return float(thrust)

    def run_steady_state(self, wind_speed: float) -> Dict[str, Any]:
        """Run a single steady-state simulation point."""
        pitch_angle = 0.0
        if wind_speed > self.rated_wind_speed:
            pitch_angle = 2.0 + 0.5 * (wind_speed - self.rated_wind_speed)

        rotor_rpm = self.calculate_rotor_rpm(wind_speed, pitch_angle)
        power = self.calculate_power(wind_speed, pitch_angle, rotor_rpm)
        thrust = self.calculate_thrust(wind_speed, pitch_angle)

        tsr = (
            (rotor_rpm * 2 * math.pi / 60.0) * (self.rotor_diameter / 2.0) / wind_speed
            if wind_speed > 0
            else 0
        )
        cp = self._calculate_cp(tsr, pitch_angle)

        return {
            "wind_speed": wind_speed,
            "rotor_rpm": rotor_rpm,
            "power_output": power,
            "power_mw": power / 1e6,
            "thrust_force": thrust,
            "thrust_kn": thrust / 1000.0,
            "pitch_angle": pitch_angle,
            "tip_speed_ratio": tsr,
            "power_coefficient": cp,
            "aerodynamic_efficiency": cp / 0.59,
            "tip_speed": rotor_rpm * math.pi * self.rotor_diameter / 60.0,
        }

    def run_parametric_sweep(
        self, start_speed: float = 3.0, end_speed: float = 25.0, step_size: float = 1.0
    ) -> List[Dict[str, Any]]:
        """Run a parametric sweep over wind speeds."""
        results = []
        wind_speeds = np.arange(start_speed, end_speed + step_size / 2, step_size)

        for ws in wind_speeds:
            result = self.run_steady_state(ws)
            results.append(result)

        return results

    def run_time_domain(
        self,
        duration: float,
        dt: float,
        wind_speed: Optional[float] = None,
        turbulence: bool = False,
    ) -> Dict[str, Any]:
        """Run a time-domain simulation."""
        if wind_speed is None:
            wind_speed = 8.0

        num_steps = int(duration / dt)
        times = np.arange(num_steps) * dt

        wind_speeds = np.full(num_steps, wind_speed)

        if turbulence:
            sigma = self.turbulence_intensity * wind_speed
            np.random.seed(42)
            turbulence_noise = np.cumsum(np.random.randn(num_steps) * sigma * np.sqrt(dt))
            turbulence_noise = turbulence_noise - turbulence_noise[0]
            wind_speeds = wind_speed + turbulence_noise * 0.1
            wind_speeds = np.maximum(wind_speeds, 0)

        power_history = np.zeros(num_steps)
        rpm_history = np.zeros(num_steps)
        thrust_history = np.zeros(num_steps)
        pitch_history = np.zeros(num_steps)

        current_pitch = 0.0

        for i, t in enumerate(times):
            ws = wind_speeds[i]

            if ws > self.rated_wind_speed:
                current_pitch = 2.0 + 0.5 * (ws - self.rated_wind_speed)
                current_pitch = min(current_pitch, 25.0)
            else:
                current_pitch = max(current_pitch - 0.1 * dt, 0.0)

            rpm = self.calculate_rotor_rpm(ws, current_pitch)
            power = self.calculate_power(ws, current_pitch, rpm)
            thrust = self.calculate_thrust(ws, current_pitch)

            power_history[i] = power
            rpm_history[i] = rpm
            thrust_history[i] = thrust
            pitch_history[i] = current_pitch

        return {
            "time": times.tolist(),
            "duration": duration,
            "dt": dt,
            "wind_speed": wind_speeds.tolist(),
            "power_mw": (power_history / 1e6).tolist(),
            "rpm": rpm_history.tolist(),
            "thrust_kn": (thrust_history / 1000.0).tolist(),
            "pitch_deg": pitch_history.tolist(),
            "mean_power_mw": np.mean(power_history) / 1e6,
            "max_power_mw": np.max(power_history) / 1e6,
            "capacity_factor": (
                np.mean(power_history) / (self.rated_power * duration) * duration
                if duration > 0
                else 0
            ),
        }

    def estimate_annual_energy(
        self, mean_wind_speed: Optional[float] = None, hours_per_year: float = 8760.0
    ) -> float:
        """Estimate annual energy production in MWh."""
        if mean_wind_speed is None:
            mean_wind_speed = 8.0

        sweep = self.run_parametric_sweep(3.0, 25.0, 0.5)

        weibull_A = mean_wind_speed
        weibull_k = 2.0

        total_energy = 0.0
        for result in sweep:
            ws = result["wind_speed"]

            k = weibull_k
            A = weibull_A
            probability = (k / A) * (ws / A) ** (k - 1) * math.exp(-((ws / A) ** k))

            energy = result["power_mw"] * probability * hours_per_year * 0.1
            total_energy += energy

        return total_energy

    def calculate_capacity_factor(self, mean_wind_speed: Optional[float] = None) -> float:
        """Calculate capacity factor for given mean wind speed."""
        sweep = self.run_parametric_sweep(3.0, 25.0, 0.5)

        if not sweep:
            return 0.0

        mean_power = np.mean([s["power_mw"] for s in sweep])
        rated_power_mw = self.rated_power / 1e6

        return mean_power / rated_power_mw if rated_power_mw > 0 else 0.0

    def get_blade_tip_position(
        self, blade_index: int, time: float, rotor_rpm: Optional[float] = None
    ) -> Tuple[float, float]:
        """Get 3D position of blade tip (for animation)."""
        if rotor_rpm is None:
            rotor_rpm = self.calculate_rotor_rpm(8.0)

        angular_velocity = rotor_rpm * 2 * math.pi / 60.0
        angle = angular_velocity * time

        blade_angle = angle + 2 * math.pi * blade_index / self.num_blades

        tip_x = self.blade_length * math.cos(blade_angle)
        tip_y = self.blade_length * math.sin(blade_angle)

        return tip_x, tip_y

    def get_animation_parameters(self, wind_speed: float) -> Dict[str, Any]:
        """Get parameters needed for animation at given wind speed."""
        rpm = self.calculate_rotor_rpm(wind_speed)
        power = self.calculate_power(wind_speed, 0, rpm)

        angular_velocity = rpm * 2 * math.pi / 60.0

        return {
            "rotor_rpm": rpm,
            "angular_velocity": angular_velocity,
            "blade_length": self.blade_length,
            "num_blades": self.num_blades,
            "hub_height": self.hub_height,
            "rotor_diameter": self.rotor_diameter,
            "power_mw": power / 1e6,
            "tip_speed": rpm * math.pi * self.rotor_diameter / 60.0,
            "tip_speed_ratio": self.tsr_optimal if rpm > 0 else 0,
        }


def load_preset(preset_name: str) -> SimulationRunner:
    """Load a preset turbine configuration."""
    base_dir = Path(__file__).parent.parent.parent / "configs" / "presets"

    preset_map = {
        "nrel_5mw": "nrel_5mw.json",
        "iea_10mw": "iea_10mw.json",
        "community_100kw": "community_100kw.json",
    }

    filename = preset_map.get(preset_name.lower(), f"{preset_name.lower()}.json")
    preset_path = base_dir / filename

    if not preset_path.exists():
        raise FileNotFoundError(f"Preset not found: {preset_name}")

    with open(preset_path) as f:
        data = json.load(f)

    config = {
        "turbine": data.get("turbine", {}),
        "aerodynamics": data.get("aerodynamics", {}),
        "control": data.get("control", {}),
        "environment": data.get("environment", {}),
    }

    return SimulationRunner(config)


def create_simple_simulation() -> SimulationRunner:
    """Create a simple simulation with default NREL 5MW parameters."""
    return SimulationRunner()
