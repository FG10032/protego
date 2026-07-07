from dataclasses import dataclass

from models.ClusterConfig import ClusterConfig
from models.DataConfig import DataConfig
from models.SparkConfig import SparkConfig


@dataclass
class Job:
    name: str
    env: str
    type: str
    engine: str
    cluster: ClusterConfig
    spark: SparkConfig
    data: DataConfig
