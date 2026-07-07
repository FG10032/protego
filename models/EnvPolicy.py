from dataclasses import dataclass
from typing import Optional


@dataclass
class EnvPolicy:
    require_dynamic_allocation_for_batch: bool = False
    max_executor_cores: Optional[int] = None
    max_executor_memory_gb: Optional[float] = None
    allowed_architectures: Optional[list[str]] = None
    preferred_architecture: Optional[str] = None
    fail_on_unknown_instance_type: bool = False
    warn_if_estimated_utilization_below: Optional[float] = None
    target_utilization: Optional[float] = None
