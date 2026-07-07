from dataclasses import dataclass

from models.EnvPolicy import EnvPolicy
from models.InstancePricing import InstancePricing


@dataclass
class Policy:
    policies: dict[str, EnvPolicy]
    pricing: dict[str, InstancePricing]
