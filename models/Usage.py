from dataclasses import dataclass
from typing import Optional


@dataclass
class Usage:
    avg_cpu_utilization: Optional[float] = None
    p95_cpu_utilization: Optional[float] = None
    avg_memory_utilization: Optional[float] = None
    runtime_hours_per_month: Optional[float] = None
