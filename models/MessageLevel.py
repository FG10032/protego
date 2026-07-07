from enum import Enum


class MessageLevel(str, Enum):
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
