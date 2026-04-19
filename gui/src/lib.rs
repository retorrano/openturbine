use bevy::prelude::*;
use bevy_egui::{egui, EguiContexts, EguiPlugin};
use egui_plot::{Line, Plot, PlotPoints};
use openturbine_rs::{SimulationResult, WindTurbineSimulation};

pub fn create_app() {
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
        .add_systems(Update, (ui_system, animation_system, physics_system, camera_preset_system, update_blades_system))
        .run();
}

#[cfg(target_arch = "wasm32")]
#[wasm_bindgen::prelude::wasm_bindgen(start)]
pub fn wasm_main() {
    console_error_panic_hook::set_once();
    console_log::init_with_level(log::Level::Info).unwrap();
    create_app();
}

pub fn create_turbine_blade(blade_length: f32) -> Mesh {
    let mut positions: Vec<[f32; 3]> = Vec::new();
    let mut normals: Vec<[f32; 3]> = Vec::new();
    let mut indices: Vec<u32> = Vec::new();

    let num_sections = 40;
    let num_points = 20;

    for i in 0..=num_sections {
        let t = i as f32 / num_sections as f32;
        let z = t * blade_length;

        let chord = 3.5 * (1.0 - t * 0.7);
        let thickness_ratio = 0.25 * (1.0 - t * 0.5);

        let twist = (12.0 * (1.0 - t)).to_radians();

        for j in 0..=num_points {
            let s = j as f32 / num_points as f32;
            let theta = s * std::f32::consts::PI * 2.0;

            let x = chord * 0.5 * theta.cos();
            let y = chord * thickness_ratio * theta.sin();

            let rx = x * twist.cos() - y * twist.sin();
            let ry = x * twist.sin() + y * twist.cos();

            positions.push([rx, z, ry]);

            let nx = theta.cos();
            let ny = theta.sin() / thickness_ratio.max(0.01);
            let len = (nx * nx + ny * ny).sqrt().max(0.001);
            let nnx = nx / len;
            let nny = ny / len;

            let rnx = nnx * twist.cos() - nny * twist.sin();
            let rny = nnx * twist.sin() + nny * twist.cos();
            normals.push([rnx, 0.0, rny]);
        }
    }

    let pts_per_section = num_points + 1;
    for i in 0..num_sections {
        for j in 0..num_points {
            let curr = (i * pts_per_section + j) as u32;
            let next = ((i + 1) * pts_per_section + j) as u32;
            let curr_next = curr + 1;
            let next_next = next + 1;

            indices.push(curr);
            indices.push(next);
            indices.push(curr_next);

            indices.push(curr_next);
            indices.push(next);
            indices.push(next_next);
        }
    }

    let mut mesh = Mesh::new(bevy::render::render_resource::PrimitiveTopology::TriangleList, bevy::render::render_asset::RenderAssetUsages::default());
    mesh.insert_attribute(Mesh::ATTRIBUTE_POSITION, positions);
    mesh.insert_attribute(Mesh::ATTRIBUTE_NORMAL, normals);
    mesh.insert_indices(bevy::render::mesh::Indices::U32(indices));

    mesh
}

#[derive(Clone, Copy, PartialEq)]
pub enum Theme {
    Dark,
    Light,
}

impl Theme {
    fn name(&self) -> &str {
        match self {
            Theme::Dark => "Dark",
            Theme::Light => "Light",
        }
    }
}

#[derive(Resource)]
pub struct SimulationState {
    pub sim: WindTurbineSimulation,
    pub wind_speed: f32,
    pub current_result: SimulationResult,
    pub history: Vec<(f64, f64)>,
    pub rpm_history: Vec<(f64, f64)>,
    pub thrust_history: Vec<(f64, f64)>,
    pub is_animating: bool,
    pub camera_preset: Option<CameraPreset>,
    pub selected_tab: usize,
    pub show_charts: bool,
    pub show_parameters: bool,
    pub show_about: bool,
    pub theme: Theme,
}

#[derive(Clone, Copy)]
pub enum CameraPreset {
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
        let mut thrust_history = Vec::new();

        for ws in 0..=30 {
            let res = sim.run_steady_state(ws as f64);
            history.push((ws as f64, res.power_output / 1e6));
            rpm_history.push((ws as f64, res.rotor_rpm));
            thrust_history.push((ws as f64, res.thrust_force / 1e3));
        }

        Self {
            sim,
            wind_speed: 8.0,
            current_result,
            history,
            rpm_history,
            thrust_history,
            is_animating: true,
            camera_preset: None,
            selected_tab: 0,
            show_charts: true,
            show_parameters: true,
            show_about: false,
            theme: Theme::Dark,
        }
    }
}

#[derive(Component)]
struct Rotor;

#[derive(Component)]
struct Blade;

#[derive(Resource)]
struct RotorAssets {
    blade_mesh: Handle<Mesh>,
    blade_material: Handle<StandardMaterial>,
}

#[derive(Component)]
struct MainCamera;

fn setup(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
) {
    commands.spawn(PbrBundle {
        mesh: meshes.add(Plane3d::default().mesh().size(1000.0, 1000.0)),
        material: materials.add(Color::srgb(0.3, 0.5, 0.3)),
        ..default()
    });

    let hub_height = 90.0;
    commands.spawn(PbrBundle {
        mesh: meshes.add(Cylinder::new(2.0, hub_height)),
        material: materials.add(Color::srgb(0.7, 0.7, 0.7)),
        transform: Transform::from_xyz(0.0, hub_height / 2.0, 0.0),
        ..default()
    });

    commands.spawn(PbrBundle {
        mesh: meshes.add(Cuboid::new(8.0, 4.0, 4.0)),
        material: materials.add(Color::srgb(0.5, 0.5, 0.5)),
        transform: Transform::from_xyz(0.0, hub_height + 2.0, 0.0),
        ..default()
    });

    let rotor_id = commands
        .spawn((
            SpatialBundle::from_transform(Transform::from_xyz(0.0, hub_height + 2.0, 4.5)),
            Rotor,
        ))
        .id();

    let hub = commands.spawn(PbrBundle {
        mesh: meshes.add(Sphere::new(2.5)),
        material: materials.add(Color::srgb(0.9, 0.8, 0.2)),
        ..default()
    }).id();
    commands.entity(rotor_id).add_child(hub);

    let blade_len = 61.5;
    let blade_mesh = meshes.add(create_turbine_blade(blade_len));

    let blade_material = materials.add(StandardMaterial {
        base_color: Color::srgb(0.92, 0.93, 0.95),
        metallic: 0.1,
        perceptual_roughness: 0.35,
        reflectance: 0.5,
        ..default()
    });

    commands.insert_resource(RotorAssets {
        blade_mesh: blade_mesh.clone(),
        blade_material: blade_material.clone(),
    });

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

    commands.spawn((
        Camera3dBundle {
            transform: Transform::from_xyz(-180.0, 100.0, 250.0).looking_at(Vec3::new(0.0, 50.0, 0.0), Vec3::Y),
            ..default()
        },
        MainCamera,
    ));
}

fn update_blades_system(
    mut commands: Commands,
    state: Res<SimulationState>,
    rotor_assets: Res<RotorAssets>,
    rotor_query: Query<Entity, With<Rotor>>,
    blade_query: Query<Entity, With<Blade>>,
    mut last_num_blades: Local<u32>,
) {
    if state.sim.turbine_config.num_blades != *last_num_blades {
        for entity in &blade_query {
            commands.entity(entity).despawn_recursive();
        }

        if let Ok(rotor_entity) = rotor_query.get_single() {
            let num_blades = state.sim.turbine_config.num_blades;
            for i in 0..num_blades {
                let angle = i as f32 * 2.0 * std::f32::consts::PI / num_blades as f32;
                let blade = commands.spawn((
                    PbrBundle {
                        mesh: rotor_assets.blade_mesh.clone(),
                        material: rotor_assets.blade_material.clone(),
                        transform: Transform::from_xyz(0.0, 0.0, 0.0)
                            .with_rotation(Quat::from_rotation_z(angle)),
                        ..default()
                    },
                    Blade,
                )).id();
                commands.entity(rotor_entity).add_child(blade);
            }
        }
        *last_num_blades = state.sim.turbine_config.num_blades;
    }
}

fn physics_system(mut state: ResMut<SimulationState>) {
    state.current_result = state.sim.run_steady_state(state.wind_speed as f64);

    let ws = state.wind_speed as f64;
    let p = state.current_result.power_output / 1e6;
    let r = state.current_result.rotor_rpm;
    let t = state.current_result.thrust_force / 1e3;

    if !state.history.iter().any(|&(w, _)| (w - ws).abs() < 0.01) {
        state.history.push((ws, p));
        state.rpm_history.push((ws, r));
        state.thrust_history.push((ws, t));
        state.history.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
        state.rpm_history.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
        state.thrust_history.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
    }
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

fn apply_theme(ctx: &egui::Context, theme: Theme) {
    let mut visuals = match theme {
        Theme::Dark => egui::Visuals::dark(),
        Theme::Light => egui::Visuals::light(),
    };

    match theme {
        Theme::Dark => {
            visuals.panel_fill = egui::Color32::from_rgb(20, 20, 20);
            visuals.window_fill = egui::Color32::from_rgb(25, 25, 25);
            visuals.override_text_color = Some(egui::Color32::WHITE);
        }
        Theme::Light => {
            visuals.panel_fill = egui::Color32::from_rgb(240, 240, 240);
            visuals.window_fill = egui::Color32::from_rgb(255, 255, 255);
            visuals.override_text_color = Some(egui::Color32::BLACK);
        }
    }

    ctx.set_visuals(visuals);
}

fn ui_system(
    mut contexts: EguiContexts,
    mut state: ResMut<SimulationState>,
    mut app_exit_events: EventWriter<AppExit>,
) {
    let ctx = contexts.ctx_mut();
    apply_theme(ctx, state.theme);

    let height = ctx.available_rect().height();

    egui::TopBottomPanel::top("menu_bar")
        .show(ctx, |ui| {
        egui::menu::bar(ui, |ui| {
            ui.menu_button("File", |ui| {
                if ui.button("New Project").clicked() { ui.close_menu(); }
                if ui.button("Open...").clicked() { ui.close_menu(); }
                ui.separator();
                if ui.button("Save").clicked() { ui.close_menu(); }
                if ui.button("Save As...").clicked() { ui.close_menu(); }
                ui.separator();
                if ui.button("Import Configuration...").clicked() { ui.close_menu(); }
                #[cfg(not(target_arch = "wasm32"))]
                if ui.button("Export Results...").clicked() {
                    let history = state.history.clone();
                    let rpm_history = state.rpm_history.clone();
                    let thrust_history = state.thrust_history.clone();

                    let files = rfd::FileDialog::new()
                        .add_filter("CSV Files", &["csv"])
                        .set_file_name("simulation_results.csv")
                        .save_file();

                    if let Some(path) = files {
                        let writer = std::fs::File::create(path).ok();
                        if let Some(mut f) = writer {
                            use std::io::Write;
                            let _ = writeln!(f, "Wind Speed (m/s),Power (MW),RPM,Thrust (kN)");
                            for i in 0..history.len() {
                                let _ = writeln!(f, "{:.1},{:.4},{:.2},{:.2}",
                                    history[i].0,
                                    history[i].1,
                                    rpm_history[i].1,
                                    thrust_history[i].1
                                );
                            }
                        }
                    }
                    ui.close_menu();
                }
                #[cfg(target_arch = "wasm32")]
                if ui.button("Export Results...").clicked() {
                    ui.close_menu();
                }
                #[cfg(not(target_arch = "wasm32"))]
                if ui.button("Export Report (PDF)...").clicked() {
                    let sim = state.sim.clone();
                    let history = state.history.clone();
                    let rpm_history = state.rpm_history.clone();
                    let thrust_history = state.thrust_history.clone();

                    let files = rfd::FileDialog::new()
                        .add_filter("PDF Files", &["pdf"])
                        .set_file_name("OpenTurbine_Report.pdf")
                        .save_file();

                    if let Some(path) = files {
                        println!("Selected PDF path: {:?}", path);
                        std::thread::spawn(move || {
                            println!("Starting PDF generation thread...");
                            export_pdf_report(&path, &sim, history, rpm_history, thrust_history);
                            println!("PDF generation thread finished.");
                        });
                    } else {
                        println!("PDF export cancelled or no path selected.");
                    }
                    ui.close_menu();
                }
                #[cfg(target_arch = "wasm32")]
                if ui.button("Export Report (PDF)...").clicked() {
                    ui.close_menu();
                }
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
                ui.menu_button("Theme", |ui| {
                    let themes = [Theme::Dark, Theme::Light];
                    for theme in themes {
                        if ui.selectable_value(&mut state.theme, theme, theme.name()).clicked() {
                            state.theme = theme;
                            ui.close_menu();
                        }
                    }
                });
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
        egui::TopBottomPanel::bottom("charts")
            .default_height(height * 0.3)
            .show(ctx, |ui| {
            ui.columns(2, |columns| {
                let power_points: PlotPoints = state.history.iter().map(|&(w, p)| [w, p]).collect();
                let line = Line::new(power_points).color(egui::Color32::from_rgb(100, 150, 250));

                columns[0].vertical(|ui| {
                    ui.label("Power Curve (MW vs m/s)");
                    Plot::new("power_plot")
                        .allow_zoom(true)
                        .allow_drag(true)
                        .show(ui, |plot_ui| plot_ui.line(line));
                });

                let rpm_points: PlotPoints = state.rpm_history.iter().map(|&(w, r)| [w, r]).collect();
                let rpm_line = Line::new(rpm_points).color(egui::Color32::from_rgb(100, 250, 150));

                columns[1].vertical(|ui| {
                    ui.label("RPM Curve (RPM vs m/s)");
                    Plot::new("rpm_plot")
                        .allow_zoom(true)
                        .allow_drag(true)
                        .show(ui, |plot_ui| plot_ui.line(rpm_line));
                });
            });
        });
    }

    if state.show_parameters {
        egui::SidePanel::left("parameters")
            .default_width(260.0)
            .show(ctx, |ui| {
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
                state.thrust_history.clear();
                let sim = state.sim.clone();
                let mut new_history = Vec::new();
                let mut new_rpm_history = Vec::new();
                let mut new_thrust_history = Vec::new();
                let mut ws = 0.0;
                while ws <= 30.0 {
                    let res = sim.run_steady_state(ws);
                    new_history.push((ws, res.power_output / 1e6));
                    new_rpm_history.push((ws, res.rotor_rpm));
                    new_thrust_history.push((ws, res.thrust_force / 1e3));
                    ws += 0.1;
                }
                state.history = new_history;
                state.rpm_history = new_rpm_history;
                state.thrust_history = new_thrust_history;
            }
        });
    }

    if state.show_about {
        egui::Window::new("About OpenTurbine").show(ctx, |ui| {
            ui.heading("OpenTurbine RS");
            ui.label("Version 0.1.2");
            ui.label("Open-source wind turbine simulation software");
            ui.label("Author: Romano E. Torrano");
            ui.label("Licensed under Apache License 2.0");
            if ui.button("Close").clicked() {
                state.show_about = false;
            }
        });
    }
}

#[cfg(not(target_arch = "wasm32"))]
fn export_pdf_report(
    path: &std::path::Path,
    sim: &openturbine_rs::WindTurbineSimulation,
    power_data: Vec<(f64, f64)>,
    rpm_data: Vec<(f64, f64)>,
    thrust_data: Vec<(f64, f64)>
) {
    use printpdf::*;
    use plotters::prelude::*;
    use std::fs::File;
    use std::io::BufWriter;

    let width_mm = 8.5 * 25.4;
    let height_mm = 13.0 * 25.4;

    println!("Creating Multi-page Long-format PdfDocument (8.5x13 in)...");
    let (doc, page1, layer1) = PdfDocument::new("OpenTurbine Simulation Report", Mm(width_mm), Mm(height_mm), "Summary Layer");
    let current_layer = doc.get_page(page1).get_layer(layer1);

    let font_path = "/usr/share/fonts/dejavu-sans-mono-fonts/DejaVuSansMono.ttf";
    let font = if std::path::Path::new(font_path).exists() {
        doc.add_external_font(File::open(font_path).expect("Failed to open font file")).expect("Failed to add external font")
    } else {
        println!("External font not found, using builtin Helvetica");
        doc.add_builtin_font(BuiltinFont::Helvetica).expect("Failed to add builtin font")
    };

    let mut y_pos = height_mm - 20.0;

    current_layer.use_text("OpenTurbine Simulation Report", 24.0, Mm(20.0), Mm(y_pos), &font);
    y_pos -= 10.0;
    current_layer.use_text(format!("Version: 0.1.2 | Date: April 19, 2026"), 12.0, Mm(20.0), Mm(y_pos), &font);
    y_pos -= 15.0;

    current_layer.use_text("Configuration Summary:", 16.0, Mm(20.0), Mm(y_pos), &font);
    y_pos -= 8.0;
    current_layer.use_text(format!("Rotor Diameter: {:.1} m | Blades: {} | Rated Power: {:.1} MW",
        sim.turbine_config.rotor_diameter, sim.turbine_config.num_blades, sim.turbine_config.rated_power / 1e6), 11.0, Mm(20.0), Mm(y_pos), &font);
    y_pos -= 15.0;

    current_layer.use_text("Simulation Results Table (from session history):", 14.0, Mm(20.0), Mm(y_pos), &font);
    y_pos -= 8.0;
    current_layer.use_text("Wind (m/s) | Power (MW) | RPM | Thrust (kN)", 10.0, Mm(20.0), Mm(y_pos), &font);
    y_pos -= 5.0;
    current_layer.use_text("--------------------------------------------", 10.0, Mm(20.0), Mm(y_pos), &font);
    y_pos -= 5.0;

    let sample_count = 25;
    let step = (power_data.len() / sample_count).max(1);
    for i in (0..power_data.len()).step_by(step) {
        if y_pos < 50.0 { break; }
        let (ws, p, r, t) = (power_data[i].0, power_data[i].1, rpm_data[i].1, thrust_data[i].1);
        current_layer.use_text(format!("{:<10.1} | {:<10.3} | {:<5.1} | {:<10.1}",
            ws, p, r, t), 9.0, Mm(20.0), Mm(y_pos), &font);
        y_pos -= 5.0;
    }

    current_layer.use_text("Citation:", 11.0, Mm(20.0), Mm(35.0), &font);
    current_layer.use_text("Torrano, R. E. (2026). OpenTurbine RS: Open-source Wind Turbine Simulation Software", 9.0, Mm(20.0), Mm(30.0), &font);
    current_layer.use_text("(Version 0.1.2). Available at: https://github.com/openturbine/openturbine-rs", 9.0, Mm(20.0), Mm(25.0), &font);

    let plots = vec![
        ("Power Curve", "Power (MW)", power_data, &BLUE),
        ("Thrust Curve", "Thrust (kN)", thrust_data, &RED),
        ("Rotor Speed", "RPM", rpm_data, &GREEN),
    ];

    let render_plot = |title: &str, label_y: &str, data: &Vec<(f64, f64)>, color: &RGBColor| -> Vec<u8> {
        let img_width = 2400;
        let img_height = 2000;
        let mut buffer = vec![0u8; img_width * img_height * 3];
        {
            let root = BitMapBackend::with_buffer(&mut buffer, (img_width as u32, img_height as u32)).into_drawing_area();
            root.fill(&WHITE).expect("Failed to fill background");

            let max_y = data.iter().map(|d| d.1).fold(0.0, f64::max).max(0.1) * 1.2;
            let max_x = data.iter().map(|d| d.0).fold(0.0, f64::max).max(30.0);

            let mut chart = ChartBuilder::on(&root)
                .caption(title, ("sans-serif", 80).into_font())
                .margin(60)
                .x_label_area_size(100)
                .y_label_area_size(120)
                .build_cartesian_2d(0f64..max_x, 0f64..max_y)
                .expect("Failed to build chart");

            chart.configure_mesh()
                .label_style(("sans-serif", 40).into_font())
                .x_desc("Wind Speed (m/s)")
                .y_desc(label_y)
                .axis_desc_style(("sans-serif", 50).into_font())
                .draw().expect("Failed to draw mesh");

            chart.draw_series(LineSeries::new(data.iter().copied(), color).point_size(8)).expect("Failed to draw series");
            root.present().expect("Failed to present");
        }
        buffer
    };

    for (title, label_y, data, color) in plots {
        let (new_page, new_layer) = doc.add_page(Mm(width_mm), Mm(height_mm), format!("{} Layer", title));
        let layer_ref = doc.get_page(new_page).get_layer(new_layer);

        println!("Rendering plot: {}", title);
        let pixels = render_plot(title, label_y, &data, color);
        let image_xobject = ImageXObject {
            width: Px(2400),
            height: Px(2000),
            color_space: ColorSpace::Rgb,
            bits_per_component: ColorBits::Bit8,
            interpolate: true,
            image_data: pixels,
            image_filter: None,
            smask: None,
            clipping_bbox: None,
        };
        let image = Image::from(image_xobject);

        image.add_to_layer(layer_ref.clone(), ImageTransform {
            translate_x: Some(Mm(6.35)),
            translate_y: Some(Mm(40.0)),
            scale_x: Some(1.0),
            scale_y: Some(1.0),
            ..Default::default()
        });

        layer_ref.use_text(format!("Figure: {}", title), 22.0, Mm(20.0), Mm(height_mm - 25.0), &font);
    }

    println!("Saving PDF to: {:?}", path);
    match File::create(path) {
        Ok(file) => {
            let mut writer = BufWriter::new(file);
            match doc.save(&mut writer) {
                Ok(_) => println!("PDF successfully saved!"),
                Err(e) => println!("Error saving PDF: {:?}", e),
            }
        },
        Err(e) => println!("Error creating file: {:?}", e),
    }
}
