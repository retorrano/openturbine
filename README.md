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

#### WebAssembly (Browser) - Complete Package

Contains: `index.html`, `openturbine_gui.js`, `openturbine_gui_bg.wasm`, and all `wasm_host` server binaries for Linux, macOS, Windows, and WASM.

| Format | Download | Size |
|--------|----------|------|
| ZIP | **[Download](https://github.com/retorrano/openturbine/releases/download/v0.1.2/openturbine_gui-0.1.2-wasm.zip)** | 10 MB |
| TAR.GZ | **[Download](https://github.com/retorrano/openturbine/releases/download/v0.1.2/openturbine_gui-0.1.2-wasm.tar.gz)** | 10 MB |

#### WASM Host Server (All Platforms) - Complete Package

Contains: `wasm_host` binaries for Linux, macOS, Windows, and WASM, plus web files (`index.html`, `openturbine_gui.js`, `openturbine_gui_bg.wasm`).

| Format | Download | Size |
|--------|----------|------|
| ZIP | **[Download](https://github.com/retorrano/openturbine/releases/download/v0.1.2/wasm_host-0.1.2-all.zip)** | 11 MB |
| TAR.GZ | **[Download](https://github.com/retorrano/openturbine/releases/download/v0.1.2/wasm_host-0.1.2-all.tar.gz)** | 11 MB |

Contains: `wasm_host-0.1.2-linux-x86_64`, `wasm_host-0.1.2-macos-x86_64`, `wasm_host-0.1.2-windows-x86_64.exe`, `wasm_host-0.1.2-wasm.wasm`

### Running the Simulation

To launch the interactive 3D GUI locally:

```bash
cargo run --release -p openturbine_gui
```

### Multi-Platform Manual Builds

You can manually build the project for different platforms:

#### Windows (Cross-compile from Linux)
```bash
cargo zigbuild --release --target x86_64-pc-windows-gnu -p openturbine_gui
```

#### Web (Chrome/Browser)
Requires `wasm-bindgen-cli`:
```bash
cargo build --release --target wasm32-unknown-unknown -p openturbine_gui
wasm-bindgen --out-dir ./out --target web target/wasm32-unknown-unknown/release/openturbine_gui.wasm
```
Serve the `./out` directory with any static file server.

### How to run the WebAssembly version locally

1. **Download and Extract**: Download the `openturbine_gui-0.1.2-wasm.zip` or `openturbine_gui-0.1.2-wasm.tar.gz` from the links above.
2. **Serve the files**: Use the included `wasm_host` binary (no Python needed):
   - **Linux/macOS**: `./wasm_host-0.1.2-linux-x86_64` or `./wasm_host-0.1.2-macos-x86_64`
   - **Windows**: `wasm_host-0.1.2-windows-x86_64.exe`
   Or use any static file server:
   - **Using Python**: `python3 -m http.server 8080`
   - **Using Node.js**: `npx serve`
3. **Open Browser**: Navigate to `http://localhost:8080` in Chrome or any modern browser.

## Parameter Configuration

The GUI provides four tabs for comprehensive turbine design:
1. **Turbine**: Rotor diameter, hub height, rated power, and environmental conditions.
2. **Structural**: Material densities and Young's Modulus for blades and tower.
3. **Control**: Pitch control logic (rated/max angles, PI gains).
4. **Presets**: Technical camera view switching.

## Contributing

Contributions are welcome! Here's how you can help:

### Ways to Contribute
- **Report Bugs**: Open an issue with a clear description and steps to reproduce
- **Suggest Features**: Open an issue with your feature idea
- **Submit Pull Requests**: 
  1. Fork the repository
  2. Create a feature branch (`git checkout -b feature/amazing-feature`)
  3. Make your changes and test thoroughly
  4. Commit with clear messages (`git commit -m 'Add amazing feature'`)
  5. Push to your branch (`git push origin feature/amazing-feature`)
  6. Open a Pull Request

### Development Tips
- Run tests: `cargo test --workspace`
- Check code formatting: `cargo fmt --check`
- Run lints: `cargo clippy --workspace`

## Roadmap

### Planned Features

#### v0.2.0 - Enhanced Physics
- [ ] Aerodynamic drag modeling
- [ ] Blade pitch optimization
- [ ] Wind shear effects
- [ ] Wake modeling for wind farms

#### v0.3.0 - Advanced GUI
- [ ] Multi-turbine visualization
- [ ] Wind field animation
- [ ] Export simulation data (CSV/JSON)
- [ ] Parameter sensitivity analysis

#### v0.4.0 - Cloud & HPC
- [ ] Cloud simulation API
- [ ] Batch processing support
- [ ] GPU acceleration (compute shaders)
- [ ] Parameter optimization suite

#### Future Goals
- [ ] OpenFAST integration
- [ ] IEC 61400 certification standards compliance
- [ ] Plugin system for custom blade profiles
- [ ] AI-assisted design optimization

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
