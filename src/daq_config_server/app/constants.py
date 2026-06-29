from enum import StrEnum


class ValidAcceptHeaders(StrEnum):
    JSON = "application/json"
    PLAIN_TEXT = "text/plain"
    RAW_BYTES = "application/octet-stream"


class EndPoints(StrEnum):
    CONFIG = "/config"
    HEALTH = "/healthz"
