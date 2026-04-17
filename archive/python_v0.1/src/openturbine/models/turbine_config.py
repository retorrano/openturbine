import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict


@dataclass
class RotorConfig:
    diameter: float = 126.0
    hub_height: float = 90.0
    number_of_blades: int = 3
    rated_power: float = 5_000_000.0
    orientation: str = "upwind"
    cone_angle: float = 2.5


@dataclass
class TowerConfig:
    height: float = 90.0
    diameter_base: float = 6.0
    diameter_top: float = 3.5
    wall_thickness_base: float = 0.027
    wall_thickness_top: float = 0.019
    material_density: float = 8500.0


@dataclass
class NacelleConfig:
    length: float = 5.6
    width: float = 2.6
    height: float = 2.6
    mass: float = 50000.0


@dataclass
class HubConfig:
    diameter: float = 3.0
    length: float = 2.0
    mass: float = 28000.0


@dataclass
class TurbineConfig:
    rotor: RotorConfig = field(default_factory=RotorConfig)
    tower: TowerConfig = field(default_factory=TowerConfig)
    nacelle: NacelleConfig = field(default_factory=NacelleConfig)
    hub: HubConfig = field(default_factory=HubConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rotor": asdict(self.rotor),
            "tower": asdict(self.tower),
            "nacelle": asdict(self.nacelle),
            "hub": asdict(self.hub)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TurbineConfig":
        return cls(
            rotor=RotorConfig(**data.get("rotor", {})),
            tower=TowerConfig(**data.get("tower", {})),
            nacelle=NacelleConfig(**data.get("nacelle", {})),
            hub=HubConfig(**data.get("hub", {}))
        )
    
    @classmethod
    def from_file(cls, filepath: str) -> "TurbineConfig":
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def save(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


@dataclass
class AerodynamicConfig:
    blade_length: float = 61.5
    chord_distribution: List[Dict[str, float]] = field(default_factory=list)
    twist_distribution: List[Dict[str, float]] = field(default_factory=list)
    
    root_airfoil: str = "cylinder"
    mid_airfoil: str = "naca63_418"
    tip_airfoil: str = "naca64_418"
    
    cut_in_wind_speed: float = 3.0
    rated_wind_speed: float = 11.4
    cut_out_wind_speed: float = 25.0
    
    max_tip_speed: float = 80.0
    max_rotor_rpm: float = 12.1
    
    cp_max: float = 0.42
    tsr_optimal: float = 7.55
    ct_rated: float = 0.80
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AerodynamicConfig":
        return cls(**data)


@dataclass
class StructuralConfig:
    blade_density: float = 3450.0
    blade_young_modulus: float = 40.0e9
    blade_poisson_ratio: float = 0.3
    
    tower_density: float = 8500.0
    tower_young_modulus: float = 210.0e9
    tower_yield_strength: float = 345.0e6
    
    gearbox_ratio: float = 97.0
    generator_inertia: float = 534.116
    
    safety_factor: float = 1.5
    sn_curve_slope: float = 10.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StructuralConfig":
        return cls(**data)


@dataclass
class ControlConfig:
    pitch_kp: float = 0.018
    pitch_ki: float = 0.002
    pitch_kd: float = 0.0
    
    min_pitch_rate: float = -8.0
    max_pitch_rate: float = 8.0
    rated_pitch_angle: float = 2.0
    
    yaw_enabled: bool = True
    yaw_kp: float = 0.001
    max_yaw_rate: float = 0.5
    
    torque_type: str = "quadratic"
    rated_torque: float = 41000.0
    rated_rpm: float = 1173.7
    
    region2_start: float = 3.0
    region2_5_start: float = 11.4
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ControlConfig":
        return cls(**data)


@dataclass
class EnvironmentConfig:
    wind_speed_mode: str = "weibull"
    constant_wind_speed: float = 8.0
    mean_wind_speed: float = 8.0
    weibull_shape: float = 2.0
    weibull_scale: float = 9.0
    
    turbulence_enabled: bool = True
    turbulence_intensity: float = 0.14
    turbulence_model: str = "kaimal"
    
    wind_shear_enabled: bool = True
    shear_exponent: float = 0.14
    roughness_length: float = 0.03
    
    air_density: float = 1.225
    temperature: float = 15.0
    
    gust_enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnvironmentConfig":
        return cls(**data)


@dataclass
class SimulationConfig:
    simulation_type: str = "steady_state"
    duration: float = 600.0
    time_step: float = 0.01
    
    wind_sweep_enabled: bool = True
    sweep_start: float = 3.0
    sweep_end: float = 25.0
    sweep_step: float = 1.0
    
    save_results: bool = True
    results_directory: str = "results"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SimulationConfig":
        return cls(**data)


@dataclass
class ProjectConfig:
    version: str = "1.0"
    name: str = "Wind Turbine Project"
    description: str = ""
    
    turbine: TurbineConfig = field(default_factory=TurbineConfig)
    aerodynamics: AerodynamicConfig = field(default_factory=AerodynamicConfig)
    structural: StructuralConfig = field(default_factory=StructuralConfig)
    control: ControlConfig = field(default_factory=ControlConfig)
    environment: EnvironmentConfig = field(default_factory=EnvironmentConfig)
    simulation: SimulationConfig = field(default_factory=SimulationConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "turbine": self.turbine.to_dict(),
            "aerodynamics": self.aerodynamics.to_dict(),
            "structural": self.structural.to_dict(),
            "control": self.control.to_dict(),
            "environment": self.environment.to_dict(),
            "simulation": self.simulation.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectConfig":
        return cls(
            version=data.get("version", "1.0"),
            name=data.get("name", "Wind Turbine Project"),
            description=data.get("description", ""),
            turbine=TurbineConfig.from_dict(data.get("turbine", {})),
            aerodynamics=AerodynamicConfig.from_dict(data.get("aerodynamics", {})),
            structural=StructuralConfig.from_dict(data.get("structural", {})),
            control=ControlConfig.from_dict(data.get("control", {})),
            environment=EnvironmentConfig.from_dict(data.get("environment", {})),
            simulation=SimulationConfig.from_dict(data.get("simulation", {}))
        )
    
    @classmethod
    def from_file(cls, filepath: str) -> "ProjectConfig":
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def save(self, filepath: str):
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
