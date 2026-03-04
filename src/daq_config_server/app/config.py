import os

import yaml
from pydantic import BaseModel

from daq_config_server.core._log import LoggingConfig

CONFIG_PATH = "/etc/config/config.yaml"


class UvicornConfig(BaseModel):
    workers: int = 2


class AppConfig(BaseModel):
    logging: LoggingConfig = LoggingConfig()
    uvicorn: UvicornConfig = UvicornConfig()


def load_config() -> AppConfig:
    if os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            data = yaml.safe_load(f)
            return AppConfig(**data)
    return AppConfig()
