# OpenTurbine (Rust)

**Open-source wind turbine simulation software for design verification and analysis.**

OpenTurbine has been rewritten in Rust to provide a high-performance, memory-safe, and natively animated simulation environment. It replaces the previous Python/C++ hybrid with a modern, unified engine.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/Build-Rust-orange.svg)]()
[![Version](https://img.shields.io/badge/Version-0.1.2-blue.svg)]()

## Current Status (v0.1.2)

### What's Working

| Feature | Status |
|---------|--------|
| Steady-state power & thrust (empirical Cp/Ct) | ✅ Functional |
| Parametric wind speed sweep | ✅ Functional |
| Time-domain simulation (basic) | ✅ Functional |
| 3D visualization with blade mesh | ✅ Functional |
| Real-time rotor animation | ✅ Functional |
| Interactive parameter sliders | ✅ Functional |
| CSV export | ✅ Functional |
| PDF report generation (desktop) | ✅ Functional |
| Camera presets | ✅ Functional |
| Dark/Light themes | ✅ Functional |
| Multi-platform builds (Linux, macOS, Windows, WASM) | ✅ Functional |
| WASM browser deployment | ✅ Functional |

### What's Visual Only (Not Yet Functional)

- **Structural parameters**: `blade_density`, `blade_young_modulus`, `tower_density`, `safety_factor` — sliders exist in GUI but have no effect on simulation output.
- **Pitch PI gains**: `pitch_kp`, `pitch_ki` — sliders exist but are not used by the pitch controller.

### Known Limitations

- Aerodynamic model uses empirical Cp/Ct formulas, not a full Blade Element Momentum (BEM) solver.
- Structural analysis not yet implemented.
- Fatigue analysis not yet implemented.
- Time-domain uses constant wind (no turbulence generation).
- No airfoil polar data import.

## Features

- **Core Engine (`core/`)**: Physics solver with empirical aerodynamic models.
  - Steady-state power and thrust calculations.
  - Parametric wind speed sweeps.
  - Time-domain simulation solver.
- **Interactive GUI (`gui/`)**: Native 3D visualization and dashboard built with **Bevy** and **egui**.
  - **3D Animation**: Real-time rotor rotation driven by physics results.
  - **Dynamic Dashboard**: Tabbed interface for Turbine, Structural, and Control parameters.
  - **Real-time Charting**: Live Power (MW) and RPM curves.
  - **View Presets**: Predefined camera views.
  - **Export**: CSV and PDF report generation.
- **WASM Host (`wasm_host/`)**: Lightweight HTTP server for browser deployment.

## Project Structure

```text
openturbine/
├── core/             # Rust physics engine library
├── gui/              # Bevy-based 3D interactive application
├── wasm_host/        # HTTP server for WASM deployment
├── Cargo.toml        # Workspace configuration
└── archive/          # Legacy Python/C++ implementation (v0.1)
```

> **Note**: For those interested in the original Python and C++ implementation, the code has been preserved in the `archive/python_v0.1/` directory.

## Getting Started

### Prerequisites

- **Rust**: Install via [rustup.rs](https://rustup.rs/)
- **System Dependencies** (for Linux/Fedora):
  ```bash
  sudo dnf install -y alsa-lib-devel systemd-devel libX11-devel libXcursor-devel libXrandr-devel libXi-devel vulkan-loader-devel mesa-libGL-devel libxkbcommon-devel
  ```

### Downloads

For the latest release **v0.1.2**:

#### Desktop Applications (GUI)

| Platform | Download | Size |
|----------|----------|------|
| macOS x86_64 | **[Download](https://github.com/retorrano/openturbine/releases/download/v0.1.2/openturbine_gui-0.1.2-macos-x86_64)** | 54 MB |
| Windows x86_64 | **[Download](https://github.com/retorrano/openturbine/releases/download/v0.1.2/openturbine_gui-0.1.2-windows-x86_64.exe)** | 102 MB |
| Linux x86_64 | **[Download](https://github.com/retorrano/openturbine/releases/download/v0.1.2/openturbine_gui-0.1.2-linux-x86_64)** | 80 MB |

#### WebAssembly (Browser)

| Format | Download | Size |
|--------|----------|------|
| ZIP | **[Download](https://github.com/retorrano/openturbine/releases/download/v0.1.2/openturbine_gui-0.1.2-wasm.zip)** | 10 MB |
| TAR.GZ | **[Download](https://github.com/retorrano/openturbine/releases/download/v0.1.2/openturbine_gui-0.1.2-wasm.tar.gz)** | 10 MB |

#### WASM Host Server (All Platforms)

| Format | Download | Size |
|--------|----------|------|
| ZIP | **[Download](https://github.com/retorrano/openturbine/releases/download/v0.1.2/wasm_host-0.1.2-all.zip)** | 11 MB |
| TAR.GZ | **[Download](https://github.com/retorrano/openturbine/releases/download/v0.1.2/wasm_host-0.1.2-all.tar.gz)** | 11 MB |

### Running Locally

```bash
# Build and run
cargo run --release -p openturbine_gui
```

### Web Deployment

1. Download `openturbine_gui-0.1.2-wasm.zip` and extract.
2. Run the included `wasm_host` binary:
   ```bash
   ./wasm_host-0.1.2-linux-x86_64   # Linux
   ./wasm_host-0.1.2-macos-x86_64   # macOS
   wasm_host-0.1.2-windows-x86_64.exe  # Windows
   ```
3. Open `http://localhost:8080`

Or use any static file server:
```bash
python3 -m http.server 8080
```

## Parameter Configuration

The GUI provides four tabs:

| Tab | Parameters | Status |
|-----|------------|--------|
| **Turbine** | Rotor diameter, hub height, num blades, rated power, cone angle, blade length, TSR, max Cp, wind speed, air density, turbulence, shear exponent | ✅ Functional |
| **Structural** | Blade density, blade Young's modulus, tower density, safety factor | 🔶 Visual only (planned for v0.1.4+) |
| **Control** | Pitch angles, pitch Kp, pitch Ki, yaw toggle | 🔶 Partial (angles work, Kp/Ki planned for v0.1.5+) |
| **Presets** | Camera view buttons | ✅ Functional |

## Release History

### v0.1.2 (Current)
- WASM support with proper `wasm_bindgen` exports
- Console panic hook for debugging
- Chart zoom/drag enabled
- wasm_host with CORS and MIME types

### v0.1.1
- Multi-platform builds (Linux, macOS, Windows, WASM)
- Versioned binary naming
- First GitHub release

### v0.1.0
- Initial Rust rewrite
- Basic 3D visualization
- Steady-state and time-domain simulation

## Development Roadmap

### v0.1.3 - Code Quality & Polish
- [ ] Clean up unused structural config warnings
- [ ] Add unit tests for core simulation
- [ ] CLI argument parsing (config file input)
- [ ] JSON config import/export
- [ ] Bug fixes and error handling improvements

### v0.1.4 - Structural Analysis (Phase 1)
- [ ] Blade root bending moment calculation: `M = F_thrust * blade_length / num_blades`
- [ ] Tower base overturning moment: `M = F_thrust * hub_height`
- [ ] Simple blade tip deflection (cantilever beam)
- [ ] Display structural results in GUI: blade root moment, tower moment

### v0.1.5 - Control System
- [ ] Implement proper PID pitch controller using `pitch_kp` and `pitch_ki`
- [ ] Add pitch rate limits
- [ ] Generator torque curve modeling
- [ ] Yaw control dynamics

### v0.1.6 - Time-Domain Improvements
- [ ] Turbulence time series generation (Mann model)
- [ ] Dynamic system response (rotor inertia)
- [ ] Wind shear profile with height
- [ ] Blade/edgewise coupling

### v0.1.7 - Aerodynamic Improvements
- [ ] Implement true BEM solver with induction factors
- [ ] Prandtl tip/hub loss corrections
- [ ] Glauert correction for heavily loaded rotors
- [ ] Aerodynamic drag model

### v0.1.8 - Fatigue & Modal Analysis
- [ ] S-N curve material database
- [ ] Rainflow cycle counting
- [ ] Miner's rule damage accumulation
- [ ] Blade and tower natural frequency estimates
- [ ] Campbell diagram generation
- [ ] Resonance warning display

### v0.1.9 - Advanced Features
- [ ] Wake modeling for wind farms
- [ ] Multi-turbine visualization
- [ ] Wind farm optimization
- [ ] Export time-series data (JSON/CSV)
- [ ] Sensitivity analysis tool

### v0.2.0 - Enhanced Physics
- [ ] Full IEC 61400 design load case automation
- [ ] Extreme load calculations
- [ ] Turbulent wind field generation
- [ ] OpenFAST integration points
- [ ] GPU acceleration for large parametric sweeps

### Future Goals
- [ ] Cloud simulation API
- [ ] Batch processing pipeline
- [ ] Optimization suite
- [ ] Plugin system for custom blade profiles
- [ ] IEC 61400 certification standards compliance

## Contributing

Contributions are welcome! Here's how you can help:

### Ways to Contribute
- **Report Bugs**: Open an issue with clear reproduction steps
- **Suggest Features**: Open an issue with your feature idea
- **Submit Pull Requests**:
  1. Fork the repository
  2. Create a feature branch (`git checkout -b feature/amazing-feature`)
  3. Make your changes and test thoroughly
  4. Commit with clear messages
  5. Push to your branch
  6. Open a Pull Request

### Development Tips
```bash
# Run tests
cargo test --workspace

# Check formatting
cargo fmt --check

# Run lints
cargo clippy --workspace
```

## Author

**Romano E. Torrano**
- Email: [romano.torrano@gmail.com](mailto:romano.torrano@gmail.com)
- Facebook: [fb.com/retorrano](https://fb.com/retorrano)

## Citation

If you use OpenTurbine in your research, please cite it as follows:

```
Romano E. Torrano. (2026). OpenTurbine (Version 0.1.2) [Computer software].
Retrieved from https://github.com/retorrano/openturbine
```

For BibTeX:
```bibtex
@misc{openturbine2026,
  author = {Romano E. Torrano},
  title = {OpenTurbine},
  year = {2026},
  version = {0.1.2},
  url = {https://github.com/retorrano/openturbine},
  note = {Open-source wind turbine simulation software}
}
```

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

---

**OpenTurbine** - Empowering wind energy innovation through open science.