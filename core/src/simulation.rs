use crate::types::*;
use std::f64::consts::PI;

#[derive(Clone)]
pub struct WindTurbineSimulation {
    pub turbine_config: TurbineConfig,
    pub aero_config: AerodynamicConfig,
    pub structural_config: StructuralConfig,
    pub control_config: ControlConfig,
    pub env_config: EnvironmentConfig,
    pub sim_config: SimulationConfig,
    pub current_time: f64,
    pub current_rotor_angle: f64,
}

impl Default for WindTurbineSimulation {
    fn default() -> Self {
        Self {
            turbine_config: TurbineConfig::default(),
            aero_config: AerodynamicConfig::default(),
            structural_config: StructuralConfig::default(),
            control_config: ControlConfig::default(),
            env_config: EnvironmentConfig::default(),
            sim_config: SimulationConfig::default(),
            current_time: 0.0,
            current_rotor_angle: 0.0,
        }
    }
}

impl WindTurbineSimulation {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn calculate_power_coefficient(&self, tsr: f64, pitch: f64) -> f64 {
        if tsr <= 0.0 || tsr >= 15.0 {
            return 0.0;
        }

        let pitch_rad = pitch * PI / 180.0;
        let mut cp = 0.22 * (116.0 / (tsr + 0.08 * pitch_rad) - 0.4 * pitch_rad - 5.0);
        
        if cp < 0.0 {
            cp = 0.0;
        } else if cp > self.aero_config.cp_max {
            cp = self.aero_config.cp_max;
        }
        
        cp
    }

    pub fn calculate_thrust_coefficient(&self, tsr: f64, _pitch: f64) -> f64 {
        if tsr <= 0.0 || tsr >= 15.0 {
            return 0.0;
        }

        let mut ct = 4.0 * (1.0 - 0.09 * tsr) / (tsr + 1.0);
        
        if ct < 0.0 {
            ct = 0.0;
        } else if ct > 1.0 {
            ct = 1.0;
        }
        
        ct
    }

    pub fn run_steady_state(&self, wind_speed: f64) -> SimulationResult {
        if wind_speed < self.aero_config.cut_in_wind_speed || wind_speed > self.aero_config.cut_out_wind_speed {
            return SimulationResult {
                wind_speed,
                rotor_rpm: 0.0,
                power_output: 0.0,
                thrust_force: 0.0,
                power_coefficient: 0.0,
                thrust_coefficient: 0.0,
                pitch_angle: 0.0,
                tip_speed_ratio: 0.0,
                aerodynamic_efficiency: 0.0,
                time_series_power: vec![],
                time_series_rpm: vec![],
                time_series_thrust: vec![],
                time_series_pitch: vec![],
            };
        }

        let rotor_radius = self.turbine_config.rotor_diameter / 2.0;
        let swept_area = PI * rotor_radius * rotor_radius;
        
        let pitch = self.control_config.rated_pitch_angle;
        
        let mut tsr = self.aero_config.tsr_optimal;
        if wind_speed > self.aero_config.rated_wind_speed {
            tsr = (self.aero_config.max_rotor_rpm * 2.0 * PI / 60.0) * rotor_radius / wind_speed;
        }
        
        let tip_speed = wind_speed * tsr;
        let rotor_rpm = tip_speed / (2.0 * PI * rotor_radius) * 60.0;
        
        let ct = self.calculate_thrust_coefficient(tsr, pitch);
        let thrust_force = 0.5 * self.env_config.air_density * swept_area * ct * wind_speed * wind_speed;
        
        let cp = self.calculate_power_coefficient(tsr, pitch);
        let mut power_output = 0.5 * self.env_config.air_density * swept_area * cp * wind_speed.powi(3);
        if power_output > self.turbine_config.rated_power {
            power_output = self.turbine_config.rated_power;
        }
        
        let aerodynamic_efficiency = cp / 0.59;

        SimulationResult {
            wind_speed,
            rotor_rpm,
            power_output,
            thrust_force,
            power_coefficient: cp,
            thrust_coefficient: ct,
            pitch_angle: pitch,
            tip_speed_ratio: tsr,
            aerodynamic_efficiency,
            time_series_power: vec![],
            time_series_rpm: vec![],
            time_series_thrust: vec![],
            time_series_pitch: vec![],
        }
    }

    pub fn run_parametric_sweep(&self) -> Vec<SimulationResult> {
        let mut results = Vec::new();
        let mut current_speed = self.sim_config.sweep_start;
        
        while current_speed <= self.sim_config.sweep_end {
            results.push(self.run_steady_state(current_speed));
            current_speed += self.sim_config.sweep_step;
        }
        
        results
    }

    pub fn run_time_domain(&mut self, duration: f64) -> SimulationResult {
        let dt = self.sim_config.time_step;
        let num_steps = (duration / dt) as usize;
        
        let mut time_series_power = vec![0.0; num_steps];
        let mut time_series_rpm = vec![0.0; num_steps];
        let mut time_series_thrust = vec![0.0; num_steps];
        let mut time_series_pitch = vec![0.0; num_steps];
        
        let wind_speed = self.env_config.mean_wind_speed;
        
        for i in 0..num_steps {
            let mut current_pitch = self.control_config.rated_pitch_angle;
            if wind_speed > self.aero_config.rated_wind_speed {
                current_pitch += 0.5 * (wind_speed - self.aero_config.rated_wind_speed);
                if current_pitch > self.control_config.max_pitch_angle {
                    current_pitch = self.control_config.max_pitch_angle;
                }
            }
            
            let rotor_radius = self.turbine_config.rotor_diameter / 2.0;
            let swept_area = PI * rotor_radius * rotor_radius;
            let tsr = self.aero_config.tsr_optimal;
            
            let tip_speed = wind_speed * tsr;
            let rpm = tip_speed / (2.0 * PI * rotor_radius) * 60.0;
            
            let ct = self.calculate_thrust_coefficient(tsr, current_pitch);
            let cp = self.calculate_power_coefficient(tsr, current_pitch);
            
            let mut power = 0.5 * self.env_config.air_density * swept_area * cp * wind_speed.powi(3);
            if power > self.turbine_config.rated_power {
                power = self.turbine_config.rated_power;
            }
            
            let thrust = 0.5 * self.env_config.air_density * swept_area * ct * wind_speed * wind_speed;
            
            time_series_power[i] = power;
            time_series_rpm[i] = rpm;
            time_series_thrust[i] = thrust;
            time_series_pitch[i] = current_pitch;
            
            self.current_rotor_angle += rpm * 2.0 * PI / 60.0 * dt;
        }
        
        let final_rpm = time_series_rpm.last().copied().unwrap_or(0.0);
        let final_power = time_series_power.last().copied().unwrap_or(0.0);
        let final_thrust = time_series_thrust.last().copied().unwrap_or(0.0);
        let final_pitch = time_series_pitch.last().copied().unwrap_or(0.0);
        
        SimulationResult {
            wind_speed,
            rotor_rpm: final_rpm,
            power_output: final_power,
            thrust_force: final_thrust,
            pitch_angle: final_pitch,
            power_coefficient: 0.0, // simplified for time domain end result here
            thrust_coefficient: 0.0,
            tip_speed_ratio: 0.0,
            aerodynamic_efficiency: 0.0,
            time_series_power,
            time_series_rpm,
            time_series_thrust,
            time_series_pitch,
        }
    }
}
