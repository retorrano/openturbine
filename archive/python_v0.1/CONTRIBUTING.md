# Contributing to OpenTurbine

Thank you for your interest in contributing to OpenTurbine! This project welcomes contributions from the community.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code. Please report unacceptable behavior to info@openturbine.org.

## How Can I Contribute?

### Reporting Bugs

Before submitting a bug report:

1. **Check the issue tracker** to see if the issue has already been reported
2. **Update to the latest version** to see if the issue persists
3. **Collect relevant information**:
   - Operating system and version
   - Python version
   - OpenTurbine version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages or logs

Submit a bug report using the [GitHub Issues](https://github.com/openturbine/openturbine/issues) with the `bug` label.

### Suggesting Features

We track feature requests using [GitHub Issues](https://github.com/openturbine/openturbine/issues) with the `enhancement` label.

Before suggesting a new feature:

1. **Search existing issues** to avoid duplicates
2. **Consider the scope** - does it fit the project's goals?
3. **Explain the use case** - why would this feature be valuable?

Feature suggestions are welcome and will be evaluated based on:
- Alignment with project goals
- Technical feasibility
- User benefit
- Maintenance implications

### Pull Requests

#### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork locally**:
   ```bash
   git clone https://github.com/your-username/openturbine.git
   cd openturbine
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/openturbine/openturbine.git
   ```
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
   or
   ```bash
   git checkout -b fix/your-bug-fix
   ```

#### Development Setup

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode with dev tools
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

#### Making Changes

1. **Keep your branch updated**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Write your code** following our style guidelines

3. **Add tests** for new functionality

4. **Run the test suite**:
   ```bash
   pytest tests/ -v
   ```

5. **Format your code**:
   ```bash
   black src/
   ```

6. **Type check**:
   ```bash
   mypy src/
   ```

7. **Commit your changes** with a clear message:
   ```bash
   git add .
   git commit -m "Add: brief description of changes
   
   - Detailed bullet points if needed
   - Reference issue number if applicable"
   ```

8. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

9. **Open a Pull Request** on GitHub

#### Pull Request Guidelines

- **Fill out the PR template** completely
- **Reference related issues** using keywords (e.g., "Closes #123")
- **Add tests** for new functionality
- **Update documentation** if needed
- **Keep PRs focused** - one feature or fix per PR
- **Be responsive** to review comments

### Code Style

#### Python

We use `black` for formatting and `mypy` for type checking.

```python
# Good
def calculate_power(
    wind_speed: float,
    rotor_diameter: float,
    air_density: float = 1.225
) -> float:
    swept_area = 3.14159 * (rotor_diameter / 2) ** 2
    return 0.5 * air_density * swept_area * wind_speed ** 3

# Bad
def calculate_power(wind_speed,rotor_diameter,air_density=1.225):
    swept_area=3.14159*(rotor_diameter/2)**2
    return 0.5*air_density*swept_area*wind_speed**3
```

#### C++

We follow the C++ Core Guidelines with some project-specific conventions:

```cpp
// Good
class WindTurbineSimulation {
public:
    explicit WindTurbineSimulation(const TurbineConfig& config);
    void initialize();
    
private:
    TurbineConfig config_;
    bool initialized_ = false;
};

// Bad
class WindTurbineSimulation{
public:
    WindTurbineSimulation(const TurbineConfig &config){
        this->config = config;
    }
private:
    TurbineConfig config;
    bool initialized;
};
```

#### Documentation

- **Docstrings** for all public functions and classes
- **Inline comments** for complex logic
- **README updates** for user-facing changes
- **API documentation** for public interfaces

### Testing Requirements

All new code must include appropriate tests:

- **Unit tests** for individual functions/methods
- **Integration tests** for module interactions
- **Validation tests** against known solutions

Minimum coverage requirements:
- New code: 80% line coverage
- Critical paths: 95% line coverage

### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, white-space (no code change)
- `refactor`: Code restructuring without behavior change
- `test`: Adding or updating tests
- `chore`: Build process, auxiliary tools

Example:
```
feat(aerodynamics): add BEM wake model implementation

Implemented Frandsen wake model for accurate near-wake simulation.
Includes turbulence intensity calculation and wake expansion factor.

Closes #45
```

## Project Governance

### Maintainers

The project is maintained by a team of volunteers. See the [MAINTAINERS](MAINTAINERS.md) file for current maintainer information.

### Decision Making

Major decisions are made by consensus among maintainers. When consensus cannot be reached, decisions may be made by a simple majority vote of active maintainers.

### Release Process

1. Feature freeze 2 weeks before release
2. Bug fix only period
3. Release candidate testing
4. Release announcement
5. Post-release documentation update

## Questions?

Feel free to reach out:

- **GitHub Discussions**: For questions about using or developing OpenTurbine
- **Email**: info@openturbine.org
- **Slack**: Join our community channel (link in README)

## Recognition

Contributors will be recognized in:
- The project's [CONTRIBUTORS](CONTRIBUTORS.md) file
- Release notes
- Our social media channels

---

Thank you for contributing to OpenTurbine! Your efforts help advance wind energy research and development.
