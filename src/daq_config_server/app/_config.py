import os

import yaml
from pydantic import BaseModel

from daq_config_server.app._log import LoggingConfig

CONFIG_PATH = "/etc/config/config.yaml"
DEFAULT_WHITELIST_PATH = "/etc/config/whitelist.yaml"


class UvicornConfig(BaseModel):
    workers: int = 2


class WhitelistConfig(BaseModel):
    config_file: str = DEFAULT_WHITELIST_PATH


class ConverterConfig(BaseModel):
    config_file: str | None = None


class AppConfig(BaseModel):
    logging: LoggingConfig = LoggingConfig()
    uvicorn: UvicornConfig = UvicornConfig()
    whitelist: WhitelistConfig = WhitelistConfig()
    converter_map: ConverterConfig = ConverterConfig()


def load_config() -> AppConfig:
    if os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            data = yaml.safe_load(f)
            return AppConfig(**data)
    return AppConfig()
