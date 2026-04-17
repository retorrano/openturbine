from typing import Tuple, Dict, Callable

UNITS = {
    "length": {
        "m": 1.0,
        "cm": 0.01,
        "mm": 0.001,
        "km": 1000.0,
        "in": 0.0254,
        "ft": 0.3048,
        "yd": 0.9144,
    },
    "mass": {
        "kg": 1.0,
        "g": 0.001,
        "t": 1000.0,
        "lb": 0.453592,
    },
    "time": {
        "s": 1.0,
        "ms": 0.001,
        "min": 60.0,
        "h": 3600.0,
    },
    "speed": {
        "m/s": 1.0,
        "km/h": 1.0 / 3.6,
        "mph": 0.44704,
        "knot": 0.514444,
    },
    "area": {
        "m²": 1.0,
        "cm²": 1e-4,
        "mm²": 1e-6,
        "km²": 1e6,
    },
    "volume": {
        "m³": 1.0,
        "cm³": 1e-6,
        "L": 0.001,
        "mL": 1e-6,
    },
    "density": {
        "kg/m³": 1.0,
        "g/cm³": 1000.0,
        "kg/L": 1000.0,
    },
    "force": {
        "N": 1.0,
        "kN": 1000.0,
        "MN": 1e6,
        "lbf": 4.44822,
    },
    "pressure": {
        "Pa": 1.0,
        "kPa": 1000.0,
        "MPa": 1e6,
        "GPa": 1e9,
        "bar": 1e5,
        "psi": 6894.76,
    },
    "energy": {
        "J": 1.0,
        "kJ": 1000.0,
        "MJ": 1e6,
        "GJ": 1e9,
        "kWh": 3.6e6,
        "MWh": 3.6e9,
    },
    "power": {
        "W": 1.0,
        "kW": 1000.0,
        "MW": 1e6,
        "GW": 1e9,
    },
    "torque": {
        "N·m": 1.0,
        "kN·m": 1000.0,
        "N·mm": 0.001,
    },
    "angle": {
        "rad": 1.0,
        "deg": 0.0174533,
        "rev": 6.28319,
    },
    "frequency": {
        "Hz": 1.0,
        "kHz": 1000.0,
        "MHz": 1e6,
        "rpm": 1.0 / 60.0,
    },
    "moment_of_inertia": {
        "kg·m²": 1.0,
        "kg·cm²": 1e-4,
        "g·cm²": 1e-7,
    },
    "viscosity": {
        "m²/s": 1.0,
        "cm²/s": 1e-4,
        "mm²/s": 1e-6,
    },
}


def get_unit_type(unit: str) -> str:
    for unit_type, units in UNITS.items():
        if unit in units:
            return unit_type
    return ""


def convert_units(value: float, from_unit: str, to_unit: str) -> float:
    from_type = get_unit_type(from_unit)
    to_type = get_unit_type(to_unit)
    
    if from_type != to_type:
        raise ValueError(f"Cannot convert between {from_type} and {to_type}")
    
    if from_type == "" or to_type == "":
        raise ValueError(f"Unknown unit: {from_unit} or {to_unit}")
    
    base_value = value * UNITS[from_type][from_unit]
    return base_value / UNITS[to_type][to_unit]


def convert_to_si(value: float, unit: str) -> Tuple[float, str]:
    unit_type = get_unit_type(unit)
    
    if unit_type == "":
        return value, unit
    
    si_unit = list(UNITS[unit_type].keys())[0]
    si_value = value * UNITS[unit_type][unit]
    
    return si_value, si_unit


def format_value(value: float, unit: str, precision: int = 3) -> str:
    if abs(value) >= 1e6:
        return f"{value / 1e6:.2f} M{unit}"
    elif abs(value) >= 1e3:
        return f"{value / 1e3:.2f} k{unit}"
    elif abs(value) >= 1 and abs(value) < 1e3:
        return f"{value:.{precision}f} {unit}"
    elif abs(value) >= 1e-3:
        return f"{value * 1e3:.{precision}f} m{unit}"
    elif abs(value) >= 1e-6:
        return f"{value * 1e6:.{precision}f} µ{unit}"
    else:
        return f"{value:.{precision}e} {unit}"


def parse_unit_string(unit_string: str) -> Tuple[float, str]:
    import re
    
    pattern = r"([+-]?\d+\.?\d*)\s*([a-zA-Z°²³·µ/]+)"
    match = re.match(pattern, unit_string.strip())
    
    if match:
        value = float(match.group(1))
        unit = match.group(2)
        return value, unit
    
    raise ValueError(f"Cannot parse unit string: {unit_string}")
