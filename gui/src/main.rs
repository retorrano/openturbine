use bevy::prelude::*;
use bevy_egui::{egui, EguiContexts, EguiPlugin};
use egui_plot::{Line, Plot, PlotPoints};
use openturbine_rs::{SimulationResult, WindTurbineSimulation};

fn main() {
    App::new()
        .add_plugins(DefaultPlugins.set(WindowPlugin {
            primary_window: Some(Window {
                title: "OpenTurbine RS - Wind Turbine Simulation".into(),
                ..default()
            }),
            ..default()
        }))
        .add_plugins(EguiPlugin)
        .insert_resource(SimulationState::default())
        .add_systems(Startup, setup)
        .add_systems(Update, (ui_system, animation_system, physics_system, camera_preset_system))
        .run();
}

#[derive(Resource)]
struct SimulationState {
    sim: WindTurbineSimulation,
    wind_speed: f32,
    current_result: SimulationResult,
    history: Vec<(f64, f64)>, // (wind_speed, power_mw)
    rpm_history: Vec<(f64, f64)>, // (wind_speed, rpm)
    is_animating: bool,
    camera_preset: Option<CameraPreset>,
    selected_tab: usize,
    show_charts: bool,
    show_parameters: bool,
    show_about: bool,
}

#[derive(Clone, Copy)]
enum CameraPreset {
    OnePointPerspective,
    Isometric,
    Front,
    Side,
    HubCloseup,
    Overview,
}

impl CameraPreset {
    fn get_camera_params(&self) -> (Vec3, Vec3) {
        match self {
            CameraPreset::OnePointPerspective => (Vec3::new(80.0, 60.0, 80.0), Vec3::new(0.0, 90.0, 0.0)),
            CameraPreset::Isometric => (Vec3::new(100.0, 100.0, 100.0), Vec3::new(0.0, 90.0, 0.0)),
            CameraPreset::Front => (Vec3::new(150.0, 90.0, 0.0), Vec3::new(0.0, 90.0, 0.0)),
            CameraPreset::Side => (Vec3::new(0.0, 90.0, 150.0), Vec3::new(0.0, 90.0, 0.0)),
            CameraPreset::HubCloseup => (Vec3::new(20.0, 95.0, 20.0), Vec3::new(0.0, 92.0, 0.0)),
            CameraPreset::Overview => (Vec3::new(180.0, 100.0, 250.0), Vec3::new(0.0, 50.0, 0.0)),
        }
    }

    fn name(&self) -> &str {
        match self {
            CameraPreset::OnePointPerspective => "1-Point Perspective",
            CameraPreset::Isometric => "Isometric",
            CameraPreset::Front => "Front View",
            CameraPreset::Side => "Side View",
            CameraPreset::HubCloseup => "Hub Close-up",
            CameraPreset::Overview => "Overview",
        }
    }
}

impl Default for SimulationState {
    fn default() -> Self {
        let sim = WindTurbineSimulation::new();
        let current_result = sim.run_steady_state(8.0);
        let mut history = Vec::new();
        let mut rpm_history = Vec::new();
        
        // Initial sweep to populate charts
        for ws in 0..=30 {
            let res = sim.run_steady_state(ws as f64);
            history.push((ws as f64, res.power_output / 1e6));
            rpm_history.push((ws as f64, res.rotor_rpm));
        }

        Self {
            sim,
            wind_speed: 8.0,
            current_result,
            history,
            rpm_history,
            is_animating: true,
            camera_preset: None,
            selected_tab: 0,
            show_charts: true,
            show_parameters: true,
            show_about: false,
        }
    }
}

#[derive(Component)]
struct Rotor;

#[derive(Component)]
struct MainCamera;

fn setup(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
) {
    // Plane
    commands.spawn(PbrBundle {
        mesh: meshes.add(Plane3d::default().mesh().size(1000.0, 1000.0)),
        material: materials.add(Color::srgb(0.3, 0.5, 0.3)),
        ..default()
    });

    // Tower
    let hub_height = 90.0;
    commands.spawn(PbrBundle {
        mesh: meshes.add(Cylinder::new(2.0, hub_height)),
        material: materials.add(Color::srgb(0.7, 0.7, 0.7)),
        transform: Transform::from_xyz(0.0, hub_height / 2.0, 0.0),
        ..default()
    });

    // Nacelle
    commands.spawn(PbrBundle {
        mesh: meshes.add(Cuboid::new(8.0, 4.0, 4.0)),
        material: materials.add(Color::srgb(0.5, 0.5, 0.5)),
        transform: Transform::from_xyz(0.0, hub_height + 2.0, 0.0),
        ..default()
    });

    // Rotor (parent for blades)
    let rotor_id = commands
        .spawn((
            SpatialBundle::from_transform(Transform::from_xyz(0.0, hub_height + 2.0, 4.5)),
            Rotor,
        ))
        .id();

    // Hub
    let hub = commands.spawn(PbrBundle {
        mesh: meshes.add(Sphere::new(2.5)),
        material: materials.add(Color::srgb(0.9, 0.8, 0.2)),
        ..default()
    }).id();
    commands.entity(rotor_id).add_child(hub);

    // Blades
    let blade_len = 61.5;
    for i in 0..3 {
        let angle = i as f32 * 2.0 * std::f32::consts::PI / 3.0;
        let blade = commands.spawn(PbrBundle {
            mesh: meshes.add(Cuboid::new(1.5, blade_len, 0.5)),
            material: materials.add(Color::srgb(0.9, 0.9, 0.9)),
            transform: Transform::from_xyz(
                (blade_len / 2.0 + 1.0) * angle.sin(),
                (blade_len / 2.0 + 1.0) * angle.cos(),
                0.0,
            )
            .with_rotation(Quat::from_rotation_z(-angle)),
            ..default()
        }).id();
        commands.entity(rotor_id).add_child(blade);
    }

    // Light
    commands.spawn(PointLightBundle {
        point_light: PointLight {
            shadows_enabled: true,
            intensity: 5_000_000.0,
            range: 500.0,
            ..default()
        },
        transform: Transform::from_xyz(100.0, 150.0, 100.0),
        ..default()
    });
    
    commands.insert_resource(AmbientLight {
        color: Color::WHITE,
        brightness: 500.0,
    });

    // Camera
    commands.spawn((
        Camera3dBundle {
            transform: Transform::from_xyz(-180.0, 100.0, 250.0).looking_at(Vec3::new(0.0, 50.0, 0.0), Vec3::Y),
            ..default()
        },
        MainCamera,
    ));
}

fn physics_system(mut state: ResMut<SimulationState>) {
    state.current_result = state.sim.run_steady_state(state.wind_speed as f64);
}

fn animation_system(
    time: Res<Time>,
    state: Res<SimulationState>,
    mut query: Query<&mut Transform, With<Rotor>>,
) {
    if state.is_animating {
        let rpm = state.current_result.rotor_rpm;
        let angular_velocity = (rpm as f32 * 2.0 * std::f32::consts::PI) / 60.0;
        for mut transform in &mut query {
            transform.rotate_z(angular_velocity * time.delta_seconds());
        }
    }
}

fn camera_preset_system(
    mut state: ResMut<SimulationState>,
    mut query: Query<&mut Transform, With<MainCamera>>,
) {
    if let Some(preset) = state.camera_preset.take() {
        let (pos, target) = preset.get_camera_params();
        for mut transform in &mut query {
            *transform = Transform::from_translation(pos).looking_at(target, Vec3::Y);
        }
    }
}

fn ui_system(
    mut contexts: EguiContexts,
    mut state: ResMut<SimulationState>,
    mut app_exit_events: EventWriter<AppExit>,
) {
    let height = contexts.ctx_mut().available_rect().height();

    egui::TopBottomPanel::top("menu_bar").show(contexts.ctx_mut(), |ui| {
        egui::menu::bar(ui, |ui| {
            ui.menu_button("File", |ui| {
                if ui.button("New Project").clicked() { ui.close_menu(); }
                if ui.button("Open...").clicked() { ui.close_menu(); }
                ui.separator();
                if ui.button("Save").clicked() { ui.close_menu(); }
                if ui.button("Save As...").clicked() { ui.close_menu(); }
                ui.separator();
                if ui.button("Import Configuration...").clicked() { ui.close_menu(); }
                if ui.button("Export Results...").clicked() { ui.close_menu(); }
                ui.separator();
                if ui.button("Exit").clicked() {
                    app_exit_events.send(AppExit::default());
                }
            });
            ui.menu_button("Edit", |ui| {
                if ui.button("Undo").clicked() { ui.close_menu(); }
                if ui.button("Redo").clicked() { ui.close_menu(); }
                ui.separator();
                if ui.button("Preferences...").clicked() { ui.close_menu(); }
            });
            ui.menu_button("Simulation", |ui| {
                if ui.button("Run Simulation (F5)").clicked() { ui.close_menu(); }
                if ui.button("Stop Simulation (F6)").clicked() { ui.close_menu(); }
                ui.separator();
                if ui.button("Parametric Sweep...").clicked() { ui.close_menu(); }
            });
            ui.menu_button("View", |ui| {
                if ui.button("Reset Layout").clicked() {
                    state.show_charts = true;
                    state.show_parameters = true;
                    ui.close_menu();
                }
                ui.separator();
                ui.checkbox(&mut state.show_parameters, "Parameters Panel");
                ui.checkbox(&mut state.show_charts, "Charts Dashboard");
                ui.separator();
                ui.menu_button("View Presets", |ui| {
                    let presets = [
                        CameraPreset::OnePointPerspective,
                        CameraPreset::Isometric,
                        CameraPreset::Front,
                        CameraPreset::Side,
                        CameraPreset::HubCloseup,
                        CameraPreset::Overview,
                    ];
                    for preset in presets {
                        if ui.button(preset.name()).clicked() {
                            state.camera_preset = Some(preset);
                            ui.close_menu();
                        }
                    }
                });
                if ui.button("Reset View (R)").clicked() {
                    state.camera_preset = Some(CameraPreset::Overview);
                    ui.close_menu();
                }
            });
            ui.menu_button("Tools", |ui| {
                if ui.button("Airfoil Editor...").clicked() { ui.close_menu(); }
                if ui.button("Wake Analysis...").clicked() { ui.close_menu(); }
                ui.separator();
                if ui.button("Compare Designs...").clicked() { ui.close_menu(); }
            });
            ui.menu_button("Help", |ui| {
                if ui.button("Tutorial...").clicked() { ui.close_menu(); }
                if ui.button("Documentation...").clicked() { ui.close_menu(); }
                ui.separator();
                if ui.button("About OpenTurbine").clicked() {
                    state.show_about = true;
                    ui.close_menu();
                }
            });
        });
    });

    if state.show_charts {
        egui::TopBottomPanel::bottom("charts").default_height(height * 0.3).show(contexts.ctx_mut(), |ui| {
            ui.columns(2, |columns| {
                let power_points: PlotPoints = state.history.iter().map(|&(w, p)| [w, p]).collect();
                let line = Line::new(power_points).color(egui::Color32::from_rgb(100, 150, 250));
                
                columns[0].vertical(|ui| {
                    ui.label("Power Curve (MW vs m/s)");
                    Plot::new("power_plot")
                        .allow_zoom(false)
                        .allow_drag(false)
                        .show(ui, |plot_ui| plot_ui.line(line));
                });

                let rpm_points: PlotPoints = state.rpm_history.iter().map(|&(w, r)| [w, r]).collect();
                let rpm_line = Line::new(rpm_points).color(egui::Color32::from_rgb(100, 250, 150));
                
                columns[1].vertical(|ui| {
                    ui.label("RPM Curve (RPM vs m/s)");
                    Plot::new("rpm_plot")
                        .allow_zoom(false)
                        .allow_drag(false)
                        .show(ui, |plot_ui| plot_ui.line(rpm_line));
                });
            });
        });
    }

    if state.show_parameters {
        egui::SidePanel::left("parameters").default_width(260.0).show(contexts.ctx_mut(), |ui| {
            ui.heading("OpenTurbine - Settings");
            
            ui.separator();
            
            ui.horizontal(|ui| {
                ui.selectable_value(&mut state.selected_tab, 0, "Turbine");
                ui.selectable_value(&mut state.selected_tab, 1, "Structural");
                ui.selectable_value(&mut state.selected_tab, 2, "Control");
                ui.selectable_value(&mut state.selected_tab, 3, "Presets");
            });

            ui.separator();

            match state.selected_tab {
                0 => {
                    ui.heading("Rotor & Aero");
                    ui.add(egui::Slider::new(&mut state.sim.turbine_config.rotor_diameter, 10.0..=250.0).text("Rotor Diameter (m)"));
                    ui.add(egui::Slider::new(&mut state.sim.turbine_config.hub_height, 20.0..=200.0).text("Hub Height (m)"));
                    ui.add(egui::Slider::new(&mut state.sim.turbine_config.num_blades, 1..=5).text("Num Blades"));
                    
                    let mut rated_mw = state.sim.turbine_config.rated_power / 1e6;
                    if ui.add(egui::Slider::new(&mut rated_mw, 0.1..=20.0).text("Rated Power (MW)")).changed() {
                        state.sim.turbine_config.rated_power = rated_mw * 1e6;
                    }
                    
                    ui.add(egui::Slider::new(&mut state.sim.turbine_config.cone_angle, 0.0..=15.0).text("Cone Angle (deg)"));
                    ui.add(egui::Slider::new(&mut state.sim.aero_config.blade_length, 5.0..=120.0).text("Blade Length (m)"));
                    ui.add(egui::Slider::new(&mut state.sim.aero_config.tsr_optimal, 1.0..=15.0).text("Optimal TSR"));
                    ui.add(egui::Slider::new(&mut state.sim.aero_config.cp_max, 0.1..=0.59).text("Max Cp"));
                    
                    ui.separator();
                    ui.heading("Environment");
                    ui.add(egui::Slider::new(&mut state.wind_speed, 0.0..=30.0).text("Wind Speed (m/s)"));
                    ui.add(egui::Slider::new(&mut state.sim.env_config.air_density, 0.8..=1.5).text("Air Density (kg/m³)"));
                    ui.add(egui::Slider::new(&mut state.sim.env_config.turbulence_intensity, 0.0..=0.5).text("Turbulence"));
                    ui.add(egui::Slider::new(&mut state.sim.env_config.shear_exponent, 0.0..=0.4).text("Shear Exp"));
                }
                1 => {
                    ui.heading("Structural Specs");
                    ui.add(egui::Slider::new(&mut state.sim.structural_config.blade_density, 1000.0..=5000.0).text("Blade Density (kg/m³)"));
                    ui.add(egui::Slider::new(&mut state.sim.structural_config.blade_young_modulus, 10e9..=100e9).text("Young's Modulus (Pa)"));
                    ui.add(egui::Slider::new(&mut state.sim.structural_config.tower_density, 5000.0..=10000.0).text("Tower Density (kg/m³)"));
                    ui.add(egui::Slider::new(&mut state.sim.structural_config.safety_factor, 1.0..=3.0).text("Safety Factor"));
                }
                2 => {
                    ui.heading("Control Logic");
                    ui.add(egui::Slider::new(&mut state.sim.control_config.rated_pitch_angle, 0.0..=10.0).text("Rated Pitch (deg)"));
                    ui.add(egui::Slider::new(&mut state.sim.control_config.max_pitch_angle, 20.0..=90.0).text("Max Pitch (deg)"));
                    ui.add(egui::Slider::new(&mut state.sim.control_config.pitch_kp, 0.0..=0.1).text("Pitch Kp"));
                    ui.add(egui::Slider::new(&mut state.sim.control_config.pitch_ki, 0.0..=0.01).text("Pitch Ki"));
                    ui.checkbox(&mut state.sim.control_config.yaw_enabled, "Yaw Enabled");
                }
                3 => {
                    ui.heading("Camera Presets");
                    let presets = [
                        CameraPreset::OnePointPerspective,
                        CameraPreset::Isometric,
                        CameraPreset::Front,
                        CameraPreset::Side,
                        CameraPreset::HubCloseup,
                        CameraPreset::Overview,
                    ];

                    for preset in presets {
                        if ui.button(preset.name()).clicked() {
                            state.camera_preset = Some(preset);
                        }
                    }
                }
                _ => {}
            }

            ui.separator();

            ui.heading("Real-time Results");
            ui.label(format!("Power: {:.2} MW", state.current_result.power_output / 1e6));
            ui.label(format!("RPM: {:.2}", state.current_result.rotor_rpm));
            ui.label(format!("Thrust: {:.2} kN", state.current_result.thrust_force / 1e3));
            
            ui.checkbox(&mut state.is_animating, "Animate Blades");

            if ui.button("Refresh Power Curve").clicked() {
                state.history.clear();
                state.rpm_history.clear();
                let sim = state.sim.clone();
                for ws in 0..=30 {
                    let res = sim.run_steady_state(ws as f64);
                    state.history.push((ws as f64, res.power_output / 1e6));
                    state.rpm_history.push((ws as f64, res.rotor_rpm));
                }
            }
        });
    }

    if state.show_about {
        egui::Window::new("About OpenTurbine").show(contexts.ctx_mut(), |ui| {
            ui.heading("OpenTurbine RS");
            ui.label("Version 0.1.0");
            ui.label("Open-source wind turbine simulation software");
            ui.label("Author: Romano E. Torrano");
            ui.label("Licensed under Apache License 2.0");
            if ui.button("Close").clicked() {
                state.show_about = false;
            }
        });
    }

    // Record history for plots (incremental updates)
    let ws = state.wind_speed as f64;
    let p = state.current_result.power_output / 1e6;
    let r = state.current_result.rotor_rpm;
    
    // Only add if wind speed is significantly different or history is empty
    if state.history.is_empty() || (state.history.iter().all(|&(w, _)| (w - ws).abs() > 0.1)) {
        state.history.push((ws, p));
        state.rpm_history.push((ws, r));
        state.history.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
        state.rpm_history.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
    }
}
