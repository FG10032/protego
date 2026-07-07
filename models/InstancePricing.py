from dataclasses import dataclass


@dataclass
class InstancePricing:
    hourly: float
    vcpu: int
    memory_gb: float
    architecture: str
