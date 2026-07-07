from dataclasses import dataclass
from typing import Optional


@dataclass
class DataConfig:
    schedule: Optional[str] = None
    input_gb_per_day: Optional[float] = None
    input_events_per_second: Optional[float] = None
