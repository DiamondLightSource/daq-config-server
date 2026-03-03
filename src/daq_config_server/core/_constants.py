from dataclasses import dataclass


@dataclass(frozen=True)
class ENDPOINTS:
    CONFIG = "/config"
    HEALTH = "/healthz"


WHITELIST_REFRESH_RATE_S = 300
WHITELIST_URL = "https://raw.githubusercontent.com/DiamondLightSource/daq-config-server/refs/heads/main/whitelist.yaml"
