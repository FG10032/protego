from dataclasses import dataclass


@dataclass
class ClusterConfig:
    instance_type: str
    workers: int
    architecture: str
