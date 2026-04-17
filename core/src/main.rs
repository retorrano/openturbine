use openturbine_rs::WindTurbineSimulation;

fn main() {
    println!("OpenTurbine RS - Open-source wind turbine simulation software");
    
    let mut sim = WindTurbineSimulation::new();
    
    println!("--- Steady State Simulation ---");
    let wind_speed = 8.0;
    let result = sim.run_steady_state(wind_speed);
    println!("Wind Speed: {} m/s", wind_speed);
    println!("Power Output: {:.2} MW", result.power_output / 1e6);
    println!("Rotor RPM: {:.2}", result.rotor_rpm);
    println!("Thrust Force: {:.2} kN", result.thrust_force / 1e3);
    
    println!("\n--- Parametric Sweep ---");
    let sweep_results = sim.run_parametric_sweep();
    for res in sweep_results {
        println!("WS: {:>4.1} m/s | Power: {:>5.2} MW | RPM: {:>5.2}", res.wind_speed, res.power_output / 1e6, res.rotor_rpm);
    }
    
    println!("\n--- Time Domain Simulation ---");
    let duration = 60.0; // 60 seconds
    let time_domain_res = sim.run_time_domain(duration);
    println!("Duration: {} s", duration);
    println!("Final Power: {:.2} MW", time_domain_res.power_output / 1e6);
    println!("Final RPM: {:.2}", time_domain_res.rotor_rpm);
}
