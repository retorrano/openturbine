use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TurbineConfig {
    pub rotor_diameter: f64,
    pub hub_height: f64,
    pub num_blades: u32,
    pub rated_power: f64,
    pub cone_angle: f64,
}

impl Default for TurbineConfig {
    fn default() -> Self {
        Self {
            rotor_diameter: 126.0,
            hub_height: 90.0,
            num_blades: 3,
            rated_power: 5e6,
            cone_angle: 2.5,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AerodynamicConfig {
    pub blade_length: f64,
    pub cut_in_wind_speed: f64,
    pub rated_wind_speed: f64,
    pub cut_out_wind_speed: f64,
    pub cp_max: f64,
    pub tsr_optimal: f64,
    pub max_rotor_rpm: f64,
}

impl Default for AerodynamicConfig {
    fn default() -> Self {
        Self {
            blade_length: 61.5,
            cut_in_wind_speed: 3.0,
            rated_wind_speed: 11.4,
            cut_out_wind_speed: 30.0,
            cp_max: 0.42,
            tsr_optimal: 7.55,
            max_rotor_rpm: 12.1,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StructuralConfig {
    pub blade_density: f64,
    pub blade_young_modulus: f64,
    pub tower_density: f64,
    pub safety_factor: f64,
}

impl Default for StructuralConfig {
    fn default() -> Self {
        Self {
            blade_density: 3450.0,
            blade_young_modulus: 40e9,
            tower_density: 8500.0,
            safety_factor: 1.5,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ControlConfig {
    pub rated_pitch_angle: f64,
    pub max_pitch_angle: f64,
    pub pitch_kp: f64,
    pub pitch_ki: f64,
    pub yaw_enabled: bool,
}

impl Default for ControlConfig {
    fn default() -> Self {
        Self {
            rated_pitch_angle: 2.0,
            max_pitch_angle: 90.0,
            pitch_kp: 0.018,
            pitch_ki: 0.002,
            yaw_enabled: true,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EnvironmentConfig {
    pub mean_wind_speed: f64,
    pub air_density: f64,
    pub turbulence_intensity: f64,
    pub shear_exponent: f64,
}

impl Default for EnvironmentConfig {
    fn default() -> Self {
        Self {
            mean_wind_speed: 8.0,
            air_density: 1.225,
            turbulence_intensity: 0.14,
            shear_exponent: 0.14,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SimulationConfig {
    pub time_step: f64,
    pub sweep_start: f64,
    pub sweep_end: f64,
    pub sweep_step: f64,
}

impl Default for SimulationConfig {
    fn default() -> Self {
        Self {
            time_step: 0.01,
            sweep_start: 3.0,
            sweep_end: 30.0,
            sweep_step: 1.0,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SimulationResult {
    pub wind_speed: f64,
    pub rotor_rpm: f64,
    pub power_output: f64,
    pub thrust_force: f64,
    pub power_coefficient: f64,
    pub thrust_coefficient: f64,
    pub pitch_angle: f64,
    pub tip_speed_ratio: f64,
    pub aerodynamic_efficiency: f64,
    #[serde(skip_serializing_if = "Vec::is_empty")]
    pub time_series_power: Vec<f64>,
    #[serde(skip_serializing_if = "Vec::is_empty")]
    pub time_series_rpm: Vec<f64>,
    #[serde(skip_serializing_if = "Vec::is_empty")]
    pub time_series_thrust: Vec<f64>,
    #[serde(skip_serializing_if = "Vec::is_empty")]
    pub time_series_pitch: Vec<f64>,
}
