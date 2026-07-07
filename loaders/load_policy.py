from pathlib import Path

from loaders.helpers import _as_dict, _from_dict, _read_yaml
from models import Policy


def load_policy(path: Path) -> Policy:
    yaml_dict = _as_dict(_read_yaml(path), str(path))
    data = {
        "policies": yaml_dict.get("policies") or {},
        "pricing": yaml_dict.get("pricing") or {},
    }
    return _from_dict(Policy, data, str(path))
