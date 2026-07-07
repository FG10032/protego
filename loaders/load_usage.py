from pathlib import Path

from loaders.helpers import _as_dict, _from_dict, _read_json
from models import Usage


def load_usage(path: Path) -> dict[str, Usage]:
    usage_dict = _as_dict(_read_json(path), str(path))
    usage = {}
    for name, body in usage_dict.items():
        where = f"{path}.usage[{name}]"
        usage[name] = _from_dict(Usage, body, where)
    return usage
