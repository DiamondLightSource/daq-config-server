from dataclasses import dataclass
from enum import StrEnum


class ValidAcceptHeaders(StrEnum):
    JSON = "application/json"
    PLAIN_TEXT = "text/plain"
    RAW_BYTES = "application/octet-stream"


@dataclass(frozen=True)
class ENDPOINTS:
    CONFIG = "/config"
    HEALTH = "/healthz"
