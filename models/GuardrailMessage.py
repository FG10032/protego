from dataclasses import dataclass

from models.MessageLevel import MessageLevel


@dataclass
class GuardrailMessage:
    code: str
    env: str
    level: MessageLevel
    cause: str
    suggestion: str
