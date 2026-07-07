from dataclasses import dataclass
from typing import Optional

from models.GuardrailMessage import GuardrailMessage


@dataclass
class JobResult:
    name: str
    env: str
    status: str  # "pass" | "warn" | "fail"
    messages: list[GuardrailMessage]
    estimated_monthly_cost: Optional[float] = None
    potential_monthly_savings: Optional[float] = None
