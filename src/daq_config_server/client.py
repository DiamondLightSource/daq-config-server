import json
from http.client import HTTPConnection
from logging import Logger, getLogger
from typing import TypeVar

from .constants import ENDPOINTS

T = TypeVar("T")


class ConfigService:
    def __init__(self, address: str, port: int, log: Logger | None = None) -> None:
        self.address = address
        self.port = port
        self._log = log if log else getLogger("daq_config_server.client")

    def _get(self, endpoint: str, param: str | None = None):
        conn = HTTPConnection(self.address, self.port)
        conn.connect()
        conn.request("GET", endpoint + (f"/{param}" if param else ""))
        resp = conn.getresponse()
        assert resp.status == 200, f"Failed to get response: {resp}"
        body = json.loads(resp.read())
        assert param in body, f"Malformed response: {body} does not contain {param}"
        resp.close()
        conn.close()
        return body[param]

    def get_beamline_param(self, param: str) -> str | int | float | bool | None:
        return self._get(ENDPOINTS.BL_PARAM, param)

    def get_feature_flag(self, param: str) -> bool | None:
        """Get the specified feature flag; returns None if it does not exist. Will check
        that the HTTP response is correct and raise an AssertionError if not."""
        return self._get(ENDPOINTS.FEATURE, param)

    def get_feature_flag_list(self) -> list[str]:
        """Get the specified feature flag; returns None if it does not exist. Will check
        that the HTTP response is correct and raise an AssertionError if not."""
        return self._get(ENDPOINTS.FEATURE)

    def best_effort_get_feature_flag(self, param: str, fallback: T = None) -> bool | T:
        """Get the specified feature flag, returns fallback value (default None) if it
        doesn't exist or if there is a connection error - in the latter case logs
        to error."""
        try:
            return self._get(ENDPOINTS.FEATURE, param)
        except (AssertionError, OSError):
            self._log.error(
                "Encountered an error reading from the config service.", exc_info=True
            )
            return fallback
