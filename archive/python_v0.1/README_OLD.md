# OpenTurbine

**Open-source wind turbine simulation software for design verification and analysis**

*Author: Romano E. Torrano*

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Build Status](https://github.com/openturbine/openturbine/actions/workflows/ci.yml/badge.svg)](https://github.com/openturbine/openturbine/actions)
[![Documentation](https://img.shields.io/badge/Documentation-latest-brightgreen.svg)](https://openturbine.readthedocs.io/)

## Overview

OpenTurbine is a comprehensive, open-source desktop application for wind turbine simulations. It provides engineers, researchers, and students with powerful tools to analyze, design, and verify wind turbine configurations through interactive simulations and real-time visualization.

## Features

### Simulation Capabilities

- **Aerodynamic Analysis**: Blade Element Momentum (BEM) theory, wake models, airfoil analysis
- **Structural Analysis**: Beam modeling, fatigue analysis, modal analysis
- **Control Systems**: Pitch control, yaw control, torque control simulation
- **Environmental Modeling**: Wind field generation, turbulence models, wind shear

### Visualization

- **3D Interactive View**: Real-time rotating turbine visualization with particle-based wind flow
- **2D Schematic View**: Detailed blade cross-sections and flow diagrams
- **Real-time Charts**: Power curves, RPM plots, efficiency metrics, time-series data

### User Experience

- **Beginner & Advanced Modes**: Simplified UI for learning, full control for experts
- **Preset Turbine Library**: NREL 5MW, IEA 10MW, and other reference turbines
- **Parametric Studies**: Sweep multiple parameters and compare results
- **Export Capabilities**: CSV, JSON, PDF reports

## Installation

### Download Binaries (Recommended)

Pre-built binaries are available for download from the [Releases](https://github.com/retorrano/openturbine/releases) page:

| Platform | File | Description |
|----------|------|-------------|
| Linux | `openturbine-X.X.X-linux` | Standalone Linux executable |
| Windows | `openturbine-X.X.X-windows.exe` | Windows installer |
| macOS | `openturbine-X.X.X-macos` | macOS application |

Simply download and run the appropriate binary for your platform.

### Prerequisites (for source installation)

- Python 3.9+
- CMake 3.20+
- C++17 compatible compiler
- Qt 6.4+ (for UI)
- VTK 9.x (for 3D visualization)

### Quick Install from Source

```bash
# Clone the repository
git clone https://github.com/retorrano/openturbine.git
cd openturbine

# Install Python dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Building Binaries from Source

```bash
# Build standalone binaries (requires PyInstaller)
./build_binary.sh 0.1.0

# This creates binaries in the dist/ folder
```

### Building from Source with CMake

```bash
# Create build directory
mkdir build && cd build

# Configure with CMake
cmake .. -DBUILD_TESTS=ON -DBUILD_PYTHON_BINDINGS=ON

# Build
cmake --build . --config Release

# Install
cmake --install .
```

### Building from Source

```bash
# Create build directory
mkdir build && cd build

# Configure with CMake
cmake .. -DBUILD_TESTS=ON -DBUILD_PYTHON_BINDINGS=ON

# Build
cmake --build . --config Release

# Install
cmake --install .
```

## Usage

### Starting the Application

```bash
# Launch the GUI
openturbine

# Or run as Python module
python -m openturbine.ui.main_window
```

### Command Line Interface

```python
from openturbine.models import ProjectConfig, SimulationResult

# Load a project
config = ProjectConfig.from_file("my_turbine.json")

# Run simulation
from openturbine.simulation import Simulator
sim = Simulator(config)
result = sim.run_steady_state(wind_speed=8.0)

print(f"Power Output: {result.get_power_mw():.2f} MW")
```

### Configuration

Default parameters are provided for all modules. Modify `configs/defaults/*.json` to customize:

```json
{
    "rotor": {
        "diameter": {"value": 126.0, "unit": "m"},
        "rated_power": {"value": 5e6, "unit": "W"}
    }
}
```

## Documentation

Detailed documentation is available at [openturbine.readthedocs.io](https://openturbine.readthedocs.io/)

- [User Guide](https://openturbine.readthedocs.io/en/latest/user_guide/)
- [API Reference](https://openturbine.readthedocs.io/en/latest/api/)
- [Theory](https://openturbine.readthedocs.io/en/latest/theory/)
- [Tutorial](https://openturbine.readthedocs.io/en/latest/tutorial/)
- [Parameter Reference](docs/parameters.md) - Complete guide to all simulation parameters

## Project Structure

```
openturbine/
├── src/
│   ├── core/                    # C++ simulation engine
│   │   ├── aerodynamics/        # BEM solver, airfoil, wake models
│   │   ├── structural/          # Beam solver, fatigue analysis
│   │   ├── control/            # PID controllers, pitch/torque
│   │   └── environmental/       # Wind field, turbulence
│   ├── ui/                     # Qt-based user interface
│   ├── models/                 # Python data models
│   └── utils/                  # Configuration, unit conversion
├── configs/
│   └── defaults/               # Default parameters for all modules
├── tests/                      # Unit and integration tests
├── docs/                       # Documentation
└── assets/                     # 3D models, airfoil data
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black src/

# Type check
mypy src/
```

## License

OpenTurbine is licensed under the Apache License 2.0 - see [LICENSE](LICENSE) for details.

## Citation

If you use OpenTurbine in your research, please cite:

```bibtex
@software{openturbine,
  title = {OpenTurbine: Open-Source Wind Turbine Simulation Software},
  author = {Romano E. Torrano},
  year = {2026},
  url = {https://github.com/retorrano/openturbine}
}
```

## Support

- **Issues**: [GitHub Issues](https://github.com/retorrano/openturbine/issues)
- **Discussions**: [GitHub Discussions](https://github.com/retorrano/openturbine/discussions)
- **Email**: romano.torrano@gmail.com

## Acknowledgments

OpenTurbine builds upon established wind turbine design methodologies including:

- NREL 5MW Reference Turbine specifications
- IEC 61400 standards
- Blade Element Momentum theory
- Industry-standard control strategies

## Roadmap

- [ ] v0.1 - Core aerodynamics with basic visualization
- [ ] v0.2 - Structural analysis and fatigue
- [ ] v0.3 - Control systems integration
- [ ] v0.4 - Environmental modeling
- [ ] v1.0 - Full feature release

See the [Project Roadmap](docs/roadmap.md) for details.

---

**OpenTurbine** - Empowering wind energy innovation through open science.
