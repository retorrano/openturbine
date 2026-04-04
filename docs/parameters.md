# OpenTurbine - Wind Turbine Simulation Parameters

This document describes all parameters available in OpenTurbine and explains how they affect simulation results.

## Table of Contents

1. [Turbine Parameters](#1-turbine-parameters)
2. [Aerodynamic Parameters](#2-aerodynamic-parameters)
3. [Control Parameters](#3-control-parameters)
4. [Environment Parameters](#4-environment-parameters)
5. [Structural Parameters](#5-structural-parameters)
6. [Parameter Effects Summary](#6-parameter-effects-summary)

---

## 1. Turbine Parameters

Turbine parameters define the physical dimensions and basic configuration of the wind turbine.

### Rotor Parameters

| Parameter | Default | Unit | Range | Description |
|-----------|---------|------|-------|-------------|
| `rotor_diameter` | 126.0 | m | 10-300 | Diameter of the rotor swept area |
| `hub_height` | 90.0 | m | 20-200 | Height of hub above ground level |
| `number_of_blades` | 3 | - | 1-5 | Number of rotor blades |
| `rated_power` | 5,000,000 | W | 10k-20M | Rated electrical power output |
| `rotor_orientation` | upwind | - | upwind/downwind | Rotor position relative to tower |
| `rotor_cone_angle` | 2.5 | deg | 0-15 | Blade cone angle (tilt) |

**Key Relationships:**
- Rotor swept area = π × (rotor_diameter/2)²
- Tip speed = rotor_rpm × π × rotor_diameter / 60
- Power = 0.5 × air_density × swept_area × Cp × wind_speed³

### Tower Parameters

| Parameter | Default | Unit | Range | Description |
|-----------|---------|------|-------|-------------|
| `height` | 90.0 | m | 20-200 | Tower height (typically = hub_height) |
| `diameter_base` | 6.0 | m | 1-15 | Tower base diameter |
| `diameter_top` | 3.5 | m | 1-10 | Tower top diameter |
| `wall_thickness_base` | 0.027 | m | 0.01-0.1 | Tower wall thickness at base |
| `wall_thickness_top` | 0.019 | m | 0.01-0.1 | Tower wall thickness at top |
| `material_density` | 8500 | kg/m³ | 1000-20000 | Tower material density (steel~8500) |

### Nacelle Parameters

| Parameter | Default | Unit | Range | Description |
|-----------|---------|------|-------|-------------|
| `length` | 5.6 | m | 1-20 | Nacelle length |
| `width` | 2.6 | m | 1-10 | Nacelle width |
| `height` | 2.6 | m | 1-10 | Nacelle height |
| `mass` | 50,000 | kg | 5k-500k | Nacelle mass |

### Hub Parameters

| Parameter | Default | Unit | Range | Description |
|-----------|---------|------|-------|-------------|
| `diameter` | 3.0 | m | 1-10 | Hub diameter |
| `length` | 2.0 | m | 0.5-5 | Hub length |
| `mass` | 28,000 | kg | 5k-100k | Hub mass (including spinner) |

---

## 2. Aerodynamic Parameters

Aerodynamic parameters control the blade geometry, airfoil properties, and performance characteristics.

### Blade Geometry

| Parameter | Default | Unit | Range | Description |
|-----------|---------|------|-------|-------------|
| `blade_length` | 61.5 | m | 5-150 | Length of each blade |
| `prebend` | 0.0 | m | 0-5 | Blade tip out-of-plane curvature |

**Chord Distribution** - Chord length at normalized positions along blade:

```
Position:  0.0    0.1    0.2    0.25   0.3    0.4    0.5    0.6    0.7    0.8    0.9    1.0
Chord(m): 3.542  4.170  4.348  4.348  4.100  3.565  3.011  2.533  2.085  1.710  1.357  0.650
```

**Twist Distribution** - Twist angle at normalized positions (negative = reduces angle of attack):

```
Position:  0.0   0.1   0.2   0.25  0.3    0.4    0.5    0.6    0.7    0.8    0.9    1.0
Twist(°): 0.0   0.0   0.0   0.0   -0.5   -2.0   -4.5   -7.5   -10.0  -12.0  -13.5  -14.5
```

### Airfoil Selection

| Parameter | Default | Options | Description |
|-----------|---------|---------|-------------|
| `root_airfoil` | cylinder | cylinder, naca0025, du97w212 | Airfoil at blade root (cylindrical) |
| `mid_airfoil` | naca63_418 | naca0012, naca63_415, du97w300 | Airfoil at mid-blade |
| `tip_airfoil` | naca64_418 | naca64_418, naca65_418, du06w200 | Airfoil at blade tip |
| `reynolds_number` | 3,000,000 | 100k-20M | Reynolds number for calculations |

### Operation Limits

| Parameter | Default | Unit | Range | Description |
|-----------|---------|------|-------|-------------|
| `cut_in_wind_speed` | 3.0 | m/s | 1-6 | Wind speed to start power production |
| `rated_wind_speed` | 11.4 | m/s | 8-25 | Wind speed at rated power |
| `cut_out_wind_speed` | 25.0 | m/s | 20-35 | Wind speed for shutdown |
| `max_tip_speed` | 80.0 | m/s | 50-120 | Maximum blade tip speed |
| `max_rotor_speed` | 12.1 | rpm | 5-25 | Maximum rotor rotational speed |

### Performance Parameters

| Parameter | Default | Unit | Range | Description |
|-----------|---------|------|-------|-------------|
| `power_coefficient_max` (Cp_max) | 0.42 | - | 0.2-0.55 | Maximum power coefficient |
| `tip_speed_ratio_optimal` (TSR) | 7.55 | - | 3-12 | Optimal tip speed ratio for max Cp |
| `thrust_coefficient` (Ct) | 0.80 | - | 0.4-1.0 | Thrust coefficient at rated operation |

**Physics:**
- **Tip Speed Ratio (TSR)** = (blade_tip_speed) / (wind_speed) = (ω × R) / V
- **Power Coefficient (Cp)** = Actual power / (Available wind power) = P / (0.5ρAV³)
- **Betz Limit** = 0.59 (theoretical maximum, ~59% of wind energy captured)
- **Thrust Coefficient (Ct)** = Thrust force / (0.5ρAV²)

### Advanced Aerodynamic Corrections

| Parameter | Default | Description |
|-----------|---------|-------------|
| `use_prandtl_tip_loss` | true | Prandtl tip loss correction (reduces Cp near tips) |
| `use_prandtl_hub_loss` | true | Prandtl hub loss correction |
| `use_glauert_correction` | true | Glauert correction for high thrust (Ct > 0.96) |
| `use_bem_turbulence` | true | Include turbulence effects in BEM solver |
| `induction_factor_iterations` | 100 | Iterations for induction factor convergence |
| `induction_factor_tolerance` | 1e-6 | Convergence tolerance |

---

## 3. Control Parameters

Control parameters define the turbine's operational strategy for power optimization and protection.

### Pitch Control

**Control Type:**
| Parameter | Default | Options | Description |
|-----------|---------|---------|-------------|
| `type` | collective | collective, individual | Collective pitches all blades same; individual allows cyclic pitch |

**PID Gains:**
| Parameter | Default | Unit | Range | Description |
|-----------|---------|------|-------|-------------|
| `kp` | 0.018 | rad/rad/s | 0.001-0.1 | Proportional gain |
| `ki` | 0.002 | rad/rad | 0-0.05 | Integral gain |
| `kd` | 0.0 | rad·s/rad | 0-1.0 | Derivative gain |

**Pitch Limits:**
| Parameter | Default | Unit | Range | Description |
|-----------|---------|------|-------|-------------|
| `min_pitch_rate` | -8.0 | deg/s | -15-0 | Minimum pitch rate (negative for protection) |
| `max_pitch_rate` | 8.0 | deg/s | 0-15 | Maximum pitch rate |
| `min_pitch_angle` | 0.0 | deg | -5-10 | Minimum angle (feathered) |
| `max_pitch_angle` | 90.0 | deg | 70-95 | Maximum angle |
| `rated_pitch_angle` | 2.0 | deg | 0-15 | Pitch angle at rated operation |

### Yaw Control

| Parameter | Default | Unit | Range | Description |
|-----------|---------|------|-------|-------------|
| `enabled` | true | - | true/false | Enable yaw control system |
| `kp` | 0.001 | rad/s/rad | 0.0001-0.01 | Proportional gain |
| `ki` | 0.0001 | rad/rad | 0-0.001 | Integral gain |
| `max_yaw_rate` | 0.5 | deg/s | 0.1-2.0 | Maximum yaw rate |
| `max_yaw_error` | 8.0 | deg | 1-20 | Maximum allowed yaw error |
| `yaw_torque_threshold` | 500 | N·m | 100-5000 | Min torque to activate yaw |

### Torque Control

**Control Strategies:**
| Type | Description |
|------|-------------|
| `constant` | Fixed torque regardless of speed |
| `linear` | Torque proportional to speed |
| `quadratic` | Torque proportional to speed² (optimal for Region 2) |
| `ipc` | Individual pitch control torque |

**Torque Parameters:**
| Parameter | Default | Unit | Range | Description |
|-----------|---------|------|-------|-------------|
| `kp` | 50.0 | N·m·s/rad | 1-500 | Proportional gain |
| `ki` | 5.0 | N·m/rad | 0-50 | Integral gain |
| `rated_torque` | 41,000 | N·m | 10k-200k | Rated generator torque |
| `rated_rpm` | 1173.7 | rpm | 500-3000 | Generator rated speed |
| `cut_in_rpm` | 700.0 | rpm | 300-1000 | Speed to start torque control |

### Operation Regions

```
Region 1:  Wind < cut_in     → Turbine idling, no power
Region 2:  cut_in < Wind < rated  → Optimal power extraction (TSR control)
Region 2.5: rated < Wind < cut_out → Rated power, pitch control
Region 3:  Wind > cut_out    → Shutdown for safety
```

| Parameter | Default | Unit | Description |
|-----------|---------|------|-------------|
| `region1_enable` | true | - | Enable Region 1 operation |
| `region2_start` | 3.0 | m/s | Region 2 start (optimal) |
| `region2_5_start` | 11.4 | m/s | Region 2.5 start (rated power) |
| `region3_start` | 25.0 | m/s | Region 3 start (shutdown) |
| `parking_mode` | feathered | feathered/active/static | Mode when stopped |

### Protection Parameters

| Parameter | Default | Unit | Range | Description |
|-----------|---------|------|-------|-------------|
| `emergency_pitch_rate` | 15.0 | deg/s | 5-30 | Emergency pitch for overspeed |
| `overspeed_threshold` | 1.1 | - | 1.0-1.3 | Overspeed as fraction of max RPM |
| `underspeed_threshold` | 0.1 | - | 0-0.5 | Underspeed as fraction of cut-in RPM |
| `grid_fault_timeout` | 5.0 | s | 0.1-30 | Grid fault response time |

---

## 4. Environment Parameters

Environment parameters define wind conditions, atmospheric properties, and site characteristics.

### Wind Speed Models

| Model | Description |
|-------|-------------|
| `constant` | Fixed wind speed value |
| `uniform` | Uniform random distribution |
| `weibull` | Weibull distribution (most common) |
| `rayleigh` | Rayleigh distribution (special Weibull case) |
| `custom` | User-defined distribution |

**Wind Speed Parameters:**
| Parameter | Default | Unit | Range | Description |
|-----------|---------|------|-------|-------------|
| `constant_wind_speed` | 8.0 | m/s | 0-40 | Constant speed (for constant mode) |
| `mean_wind_speed` | 8.0 | m/s | 0-40 | Mean for Weibull/Rayleigh |
| `weibull_shape_factor` (k) | 2.0 | - | 1-4 | Shape parameter (k=2 for Rayleigh) |
| `weibull_scale_factor` (A) | 9.0 | m/s | 1-50 | Scale parameter |
| `wind_speed_min` | 0.0 | m/s | 0-10 | Minimum for simulation |
| `wind_speed_max` | 30.0 | m/s | 15-50 | Maximum for simulation |

### Turbulence Parameters

| Parameter | Default | Unit | Range | Description |
|-----------|---------|------|-------|-------------|
| `enabled` | true | - | true/false | Enable turbulent wind simulation |
| `turbulence_model` | kaimal | kaimal/von_karmaniemann/custom | Turbulence spectrum model |
| `turbulence_intensity` | 0.14 | - | 0-0.5 | IEC Class B = 0.14 |
| `turbulence_length_scale` | 340.2 | m | 10-1000 | Integral length scale |
| `coherence_model` | ieee | ieee/exponential/none | Spatial coherence model |

### Wind Shear

Wind speed increases with height due to ground friction effects.

**Shear Laws:**
| Law | Formula | Use Case |
|-----|---------|----------|
| `power` | V(h) = V(href) × (h/href)^α | Most terrain |
| `logarithmic` | V(h) = (u*/κ) × ln(h/z₀) | Open terrain |
| `none` | V(h) = constant | No shear |

| Parameter | Default | Unit | Range | Description |
|-----------|---------|------|-------|-------------|
| `shear_law` | power | - | power/logarithmic/none | Shear model |
| `power_shear_exponent` (α) | 0.14 | - | 0-0.4 | IEC Class 1=0.20, 2=0.14, 3=0.11 |
| `roughness_length` (z₀) | 0.03 | m | 0.0001-2.0 | Surface roughness |
| `reference_height` | 90.0 | m | 10-200 | Measurement height |

### Air Properties

| Parameter | Default | Unit | Range | Description |
|-----------|---------|------|-------|-------------|
| `air_density` (ρ) | 1.225 | kg/m³ | 0.8-1.5 | Air density (ISA sea level = 1.225) |
| `temperature` | 15.0 | °C | -40-50 | Air temperature |
| `pressure` | 101325 | Pa | 80k-120k | Atmospheric pressure |
| `kinematic_viscosity` (ν) | 1.5e-5 | m²/s | 1e-6-1e-4 | Dynamic viscosity |

**Density affects:**
- Available power ∝ ρ × V³
- Reynolds number ∝ ρ × V × c / μ
- Higher altitude → lower ρ → lower power

### Wind Direction

| Parameter | Default | Unit | Range | Description |
|-----------|---------|------|-------|-------------|
| `mean_direction` | 0.0 | deg | 0-360 | Mean wind direction (0=North, 90=East) |
| `direction_spread` | 15.0 | deg | 0-60 | Direction standard deviation |
| `veer` | 0.0 | deg/m | -1-1 | Direction change with height |

### Extreme Events

| Parameter | Default | Unit | Description |
|-----------|---------|------|-------------|
| `gust_enabled` | true | - | Enable extreme gusts |
| `eog_gust_speed` | 21.0 | m/s | Extreme Operating Gust amplitude |
| `eog_gust_duration` | 10.0 | s | EOG duration |
| `ecd_enabled` | true | - | Enable ECD events |
| `ecd_direction_change` | 180.0 | deg | Direction change magnitude |

### Terrain Parameters

| Parameter | Default | Options | Description |
|-----------|---------|---------|-------------|
| `terrain_type` | offshore | flat/hills/forest/offshore/coastal | Terrain classification |
| `terrain_roughness` | 0.0002 | m | Surface roughness |
| `hill_height` | 0.0 | m | Hill height for complex terrain |
| `hill_length` | 0.0 | m | Hill horizontal length |

---

## 5. Structural Parameters

Structural parameters define material properties and structural characteristics for fatigue and load analysis.

### Blade Material

| Parameter | Default | Options | Description |
|-----------|---------|---------|-------------|
| `material` | glass_fiber_epoxy | glass_fiber_epoxy/carbon_fiber_epoxy/steel/aluminum | Blade composite |
| `density` (ρ) | 3450 | kg/m³ | Material density |
| `young_modulus` (E) | 40.0×10⁹ | Pa | Young's modulus (longitudinal) |
| `poisson_ratio` (ν) | 0.3 | - | Poisson's ratio |

**Modal Frequencies:**
| Parameter | Default | Unit | Description |
|-----------|---------|------|-------------|
| `first_bending_frequency` | 0.82 | Hz | First flapwise bending |
| `second_bending_frequency` | 2.5 | Hz | Second flapwise bending |
| `edge_frequency` | 1.0 | Hz | First edgewise bending |

### Tower Material

| Parameter | Default | Unit | Description |
|-----------|---------|------|-------------|
| `material` | steel | steel/concrete/hybrid | Tower construction |
| `density` | 8500 | kg/m³ | Material density |
| `young_modulus` | 210×10⁹ | Pa | Young's modulus |
| `yield_strength` | 345×10⁶ | Pa | Material yield strength |
| `first_frequency` | 0.32 | Hz | First tower natural frequency |
| `second_frequency` | 0.85 | Hz | Second tower frequency |

### Drivetrain

| Parameter | Default | Unit | Range | Description |
|-----------|---------|------|-------|-------------|
| `gearbox_ratio` | 97.0 | - | 10-200 | Rotor to generator ratio |
| `generator_inertia` | 534.116 | kg·m² | 10-5000 | Generator rotor inertia |
| `hss_damping` | 0.0 | N·m·s/rad | 0-1000 | High-speed shaft damping |
| `lss_damping` | 27.78 | N·m·s/rad | 0-1000 | Low-speed shaft damping |

### Safety Factors

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `safety_factor` | 1.5 | 1-5 | Overall structural safety |
| `blade_safety_factor` | 2.0 | 1-5 | Blade design safety |
| `tower_safety_factor` | 1.5 | 1-5 | Tower design safety |

### Fatigue Parameters

| Parameter | Default | Unit | Description |
|-----------|---------|------|-------------|
| `sn_curve_slope` | 10.0 | - | S-N curve slope (log-log region) |
| `sn_curve_intercept` | 1.0×10⁸ | cycles | Fatigue strength at 10³ cycles |
| `damage_equivalent_factor` | 1.0 | - | DEL factor |
| `miners_sum_target` | 1.0 | - | Target fatigue life (1.0 = design life) |

---

## 6. Parameter Effects Summary

### Parameters That Affect Power Output

| Parameter | Effect | Typical Impact |
|-----------|--------|----------------|
| **blade_length** | Swept area ∝ L² | 2×L → 4× power |
| **Cp_max** | Directly scales power | 0.3→0.42 Cp → 40% more power |
| **air_density** | Power ∝ ρ | ρ 0.8→1.225 → 53% more power |
| **wind_speed** | Power ∝ V³ | V 8→12 → 2.4× power |
| **TSR_optimal** | Affects Cp curve peak | Optimal TSR maximizes Cp |
| **num_blades** | Peak Cp ∝ f(blades) | 2-blade ~0.47, 3-blade ~0.42, 4-blade ~0.38 |
| **rated_power** | Caps maximum output | Power cannot exceed rated |
| **cut_in/cut_out** | Operating range | Outside range = no power |

### Parameters That Affect Thrust

| Parameter | Effect |
|-----------|--------|
| **Ct (thrust_coefficient)** | Thrust = 0.5 × ρ × A × Ct × V² |
| **blade geometry** | Affects induced velocities |
| **wind_speed** | Thrust ∝ V² |
| **axial induction** | Links to Cp via momentum theory |

### Parameters for Structural Analysis (Currently Visual Only)

These parameters are stored but not used in power calculations:

- All structural material properties (density, Young's modulus, etc.)
- Fatigue parameters (S-N curves, Miner's sum)
- Tower frequencies
- Blade modal properties
- Safety factors

### Simulation Modes

| Mode | Description | Parameters Used |
|------|-------------|----------------|
| **Steady State** | Single operating point | wind_speed, blade_length, Cp_max, TSR, air_density |
| **Parametric Sweep** | Multiple wind speeds | Same as steady state |
| **Time Domain** | Dynamic simulation | Adds turbulence, pitch/torque control |

---

## Configuration File Format

All parameters use JSON format with standardized structure:

```json
{
    "parameter_name": {
        "value": 123.45,
        "unit": "m/s",
        "description": "Description of what this parameter does",
        "min": 0.0,
        "max": 200.0,
        "ui_group": "Category Name"
    }
}
```

### Available Presets

| Preset | Description | Rated Power | Rotor Diameter |
|--------|-------------|-------------|----------------|
| `nrel_5mw` | NREL 5MW reference turbine | 5 MW | 126 m |
| `iea_10mw` | IEA 10MW reference turbine | 10 MW | 198 m |
| `community` | Small community turbine | 100 kW | 19 m |

---

## Quick Reference: Commonly Modified Parameters

For users who want to quickly explore effects:

1. **Increase power output:**
   - Increase `blade_length` or `rotor_diameter`
   - Increase `Cp_max` (max 0.59 - Betz limit)
   - Increase `air_density` (or lower altitude)

2. **Match a specific turbine:**
   - Set `rated_power` to rated output
   - Set `rotor_diameter` to physical size
   - Set `blade_length` to blade length
   - Set `num_blades` to 2, 3, or more

3. **Simulate different wind sites:**
   - Set `mean_wind_speed` for average wind
   - Set `weibull_shape_factor` (k=2 typical)
   - Set `turbulence_intensity` (0.14 = IEC Class B)

4. **Change operational range:**
   - Adjust `cut_in_wind_speed` (typically 3-4 m/s)
   - Adjust `rated_wind_speed` (typically 11-12 m/s)
   - Adjust `cut_out_wind_speed` (typically 25 m/s)
