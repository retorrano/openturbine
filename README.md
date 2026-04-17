# OpenTurbine (Rust)

**Open-source wind turbine simulation software for design verification and analysis.**

OpenTurbine has been rewritten in Rust to provide a high-performance, memory-safe, and natively animated simulation environment. It replaces the previous Python/C++ hybrid with a modern, unified engine.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/Build-Rust-orange.svg)]()

## Features

- **Core Engine (`core/`)**: High-performance physics solver implementing Blade Element Momentum (BEM) theory.
  - Steady-state power and thrust calculations.
  - Parametric wind speed sweeps.
  - Time-domain simulation solver.
- **Interactive GUI (`gui/`)**: Native 3D visualization and dashboard built with **Bevy** and **egui**.
  - **3D Animation**: Real-time rotor rotation driven by physics results.
  - **Dynamic Dashboard**: Tabbed interface for Turbine, Structural, and Control parameters.
  - **Real-time Charting**: Live Power (MW) and RPM curves that update as you tune the model.
  - **View Presets**: Predefined technical camera views (Isometric, Hub Close-up, etc.).

## Project Structure

```text
openturbine/
├── core/             # Rust physics engine library
├── gui/              # Bevy-based 3D interactive application
├── Cargo.toml        # Workspace configuration
└── archive/          # Legacy Python/C++ implementation (v0.1)
```

## Getting Started

### Prerequisites

- **Rust**: Install via [rustup.rs](https://rustup.rs/)
- **System Dependencies** (for Linux/Fedora):
  ```bash
  sudo dnf install -y alsa-lib-devel systemd-devel libX11-devel libXcursor-devel libXrandr-devel libXi-devel vulkan-loader-devel mesa-libGL-devel libxkbcommon-devel
  ```

### Running the Simulation

To launch the interactive 3D GUI:

```bash
cargo run --release -p openturbine_gui
```

## Parameter Configuration

The GUI provides four tabs for comprehensive turbine design:
1. **Turbine**: Rotor diameter, hub height, rated power, and environmental conditions.
2. **Structural**: Material densities and Young's Modulus for blades and tower.
3. **Control**: Pitch control logic (rated/max angles, PI gains).
4. **Presets**: Technical camera view switching.

## Author

**Romano E. Torrano**
- Email: [romano.torrano@gmail.com](mailto:romano.torrano@gmail.com)
- Facebook: [fb.com/retorrano](https://fb.com/retorrano)

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

---
**OpenTurbine** - Empowering wind energy innovation through open science.
