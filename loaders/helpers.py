import json
from pathlib import Path
from typing import Any, TypeVar

import dacite
import yaml

from exceptions import ConfigError

T = TypeVar("T")

# check_types=False keeps YAML's int->float (for memory_gb converting) working.
_CONFIG = dacite.Config(check_types=False)


def _from_dict(data_class: type[T], value: Any, where: str) -> T:
    try:
        return dacite.from_dict(data_class, _as_dict(value, where), config=_CONFIG)
    except dacite.DaciteError as e:
        raise ConfigError(f"{where}: {e}") from e


def _as_dict(value: Any, where: str) -> dict:
    if not isinstance(value, dict):
        raise ConfigError(f"{where}: expected a mapping, got {type(value).__name__}")
    return value


def _read_yaml(path: Path) -> Any:
    if not path.exists():
        raise ConfigError(f"file not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except Exception as e:
        raise ConfigError(f"{path}: could not read YAML: {e}") from e


def _read_json(path: Path) -> Any:
    if not path.exists():
        raise ConfigError(f"file not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        raise ConfigError(f"{path}: could not read JSON: {e}") from e
