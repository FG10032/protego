from dataclasses import dataclass
from typing import Optional


@dataclass
class SparkConfig:
    executor_cores: int
    executor_memory_gb: float
    dynamic_allocation: bool
    max_executors: Optional[int] = None
