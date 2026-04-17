import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


def get_default_config_path() -> Path:
    base_dir = Path(__file__).parent.parent.parent.parent
    return base_dir / "configs" / "defaults"


def load_config(module: str) -> Dict[str, Any]:
    config_path = get_default_config_path() / f"{module}.json"
    
    if not config_path.exists():
        return {}
    
    with open(config_path, 'r') as f:
        return json.load(f)


def load_all_configs() -> Dict[str, Dict[str, Any]]:
    return {
        "turbine": load_config("turbine"),
        "aerodynamics": load_config("aerodynamics"),
        "structural": load_config("structural"),
        "control": load_config("control"),
        "environment": load_config("environment"),
        "simulation": load_config("simulation")
    }


def save_config(module: str, config: Dict[str, Any], output_dir: Optional[Path] = None):
    if output_dir is None:
        output_dir = get_default_config_path()
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / f"{module}.json"
    
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)


def get_default_config() -> Dict[str, Any]:
    configs = load_all_configs()
    
    return {
        "version": "1.0",
        "name": "Default Wind Turbine",
        "modules": configs
    }


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result


def validate_config(config: Dict[str, Any]) -> bool:
    required_fields = ["version", "name"]
    
    for field in required_fields:
        if field not in config:
            return False
    
    return True


def get_parameter_value(params: Dict[str, Any], path: str, default: Any = None) -> Any:
    keys = path.split(".")
    
    value = params
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    if isinstance(value, dict) and "value" in value:
        return value["value"]
    
    return value


def set_parameter_value(params: Dict[str, Any], path: str, value: Any):
    keys = path.split(".")
    
    current = params
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    final_key = keys[-1]
    
    if isinstance(current.get(final_key), dict) and "value" in current[final_key]:
        current[final_key]["value"] = value
    else:
        current[final_key] = value
