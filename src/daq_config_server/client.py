from logging import Logger, getLogger
from typing import Any, TypeVar

import requests

from .constants import ENDPOINTS

T = TypeVar("T")
BlParamDType = str | int | float | bool


class ConfigServer:
    def __init__(self, url: str, log: Logger | None = None) -> None:
        self._url = url.rstrip("/")
        self._log = log if log else getLogger("daq_config_server.client")

    def _get(
        self,
        endpoint: str,
        item: str | None = None,
    ):
        r = requests.get(self._url + endpoint + (f"/{item}" if item else ""))
        return r.json()

    def read_unformatted_file(self, file_path: str) -> Any:
        # After https://github.com/DiamondLightSource/daq-config-server/issues/67, we
        # can get specific formats, and then have better typing on
        # return values
        return self._get(ENDPOINTS.CONFIG, file_path)
