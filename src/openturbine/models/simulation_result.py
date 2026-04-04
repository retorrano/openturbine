import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
import numpy as np


@dataclass
class SimulationResult:
    wind_speed: float = 0.0
    rotor_rpm: float = 0.0
    power_output: float = 0.0
    thrust_force: float = 0.0
    power_coefficient: float = 0.0
    thrust_coefficient: float = 0.0
    pitch_angle: float = 0.0
    tip_speed_ratio: float = 0.0
    aerodynamic_efficiency: float = 0.0
    
    blade_loads: List[float] = field(default_factory=list)
    blade_deflections: List[float] = field(default_factory=list)
    tower_deflection: float = 0.0
    
    time_series_power: List[float] = field(default_factory=list)
    time_series_rpm: List[float] = field(default_factory=list)
    time_series_thrust: List[float] = field(default_factory=list)
    time_series_pitch: List[float] = field(default_factory=list)
    
    timestamp: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationResult":
        return cls(
            wind_speed=data.get("wind_speed", 0.0),
            rotor_rpm=data.get("rotor_rpm", 0.0),
            power_output=data.get("power_output", 0.0),
            thrust_force=data.get("thrust_force", 0.0),
            power_coefficient=data.get("power_coefficient", 0.0),
            thrust_coefficient=data.get("thrust_coefficient", 0.0),
            pitch_angle=data.get("pitch_angle", 0.0),
            tip_speed_ratio=data.get("tip_speed_ratio", 0.0),
            aerodynamic_efficiency=data.get("aerodynamic_efficiency", 0.0),
            blade_loads=data.get("blade_loads", []),
            blade_deflections=data.get("blade_deflections", []),
            tower_deflection=data.get("tower_deflection", 0.0),
            time_series_power=data.get("time_series_power", []),
            time_series_rpm=data.get("time_series_rpm", []),
            time_series_thrust=data.get("time_series_thrust", []),
            time_series_pitch=data.get("time_series_pitch", []),
            timestamp=data.get("timestamp")
        )
    
    def save(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> "SimulationResult":
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def get_power_mw(self) -> float:
        return self.power_output / 1_000_000.0
    
    def get_thrust_kn(self) -> float:
        return self.thrust_force / 1000.0
    
    def get_mean_power_mw(self) -> float:
        if self.time_series_power:
            return np.mean(self.time_series_power) / 1_000_000.0
        return self.get_power_mw()
    
    def get_max_power_mw(self) -> float:
        if self.time_series_power:
            return np.max(self.time_series_power) / 1_000_000.0
        return self.get_power_mw()
    
    def get_capacity_factor(self, rated_power: float) -> float:
        mean_power = self.get_mean_power_mw() * 1_000_000.0
        return mean_power / rated_power if rated_power > 0 else 0.0


@dataclass
class ParametricSweepResult:
    results: List[SimulationResult] = field(default_factory=list)
    
    wind_speeds: List[float] = field(default_factory=list)
    power_curve: List[float] = field(default_factory=list)
    rpm_curve: List[float] = field(default_factory=list)
    thrust_curve: List[float] = field(default_factory=list)
    cp_curve: List[float] = field(default_factory=list)
    
    def add_result(self, result: SimulationResult):
        self.results.append(result)
        self.wind_speeds.append(result.wind_speed)
        self.power_curve.append(result.get_power_mw())
        self.rpm_curve.append(result.rotor_rpm)
        self.thrust_curve.append(result.get_thrust_kn())
        self.cp_curve.append(result.power_coefficient)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "wind_speeds": self.wind_speeds,
            "power_curve": self.power_curve,
            "rpm_curve": self.rpm_curve,
            "thrust_curve": self.thrust_curve,
            "cp_curve": self.cp_curve,
            "results": [r.to_dict() for r in self.results]
        }
    
    def save(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> "ParametricSweepResult":
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        sweep = cls()
        sweep.wind_speeds = data.get("wind_speeds", [])
        sweep.power_curve = data.get("power_curve", [])
        sweep.rpm_curve = data.get("rpm_curve", [])
        sweep.thrust_curve = data.get("thrust_curve", [])
        sweep.cp_curve = data.get("cp_curve", [])
        sweep.results = [SimulationResult.from_dict(r) for r in data.get("results", [])]
        return sweep
    
    def get_annual_energy_mwh(self, hours_per_year: float = 8760.0) -> float:
        return sum(self.power_curve) / len(self.power_curve) * hours_per_year if self.power_curve else 0.0
