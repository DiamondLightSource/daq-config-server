import json
from http.client import HTTPConnection, HTTPSConnection
from logging import Logger, getLogger
from typing import TypeVar
from urllib3.util import parse_url
from .constants import ENDPOINTS

T = TypeVar("T")


class ConfigServer:
    def __init__(self, url: str, log: Logger | None = None) -> None:
        self._url = parse_url(url)
        if self._url.scheme != "http" and self._url.scheme != "https":
            raise ValueError("ConfigServer must use HTTP or HTTPS!")
        self._Conn = HTTPSConnection if self._url.scheme == "https" else HTTPConnection
        self._log = log if log else getLogger("daq_config_server.client")

    def _get(self, endpoint: str, item: str | None = None):
        req_item = f"/{item}" if item else ""
        conn = self._Conn(self._url.host, self._url.port or self._url.scheme)
        conn.connect()
        conn.request("GET", self._url.request_uri + endpoint + req_item)
        resp = conn.getresponse()
        assert resp.status == 200, f"Failed to get response: {resp!r}"
        body = json.loads(resp.read())
        assert item in body, f"Malformed response: {body} does not contain {item}"
        resp.close()
        conn.close()
        return body[item]

    def get_beamline_param(self, param: str) -> str | int | float | bool | None:
        return self._get(ENDPOINTS.BL_PARAM, param)

    def get_feature_flag(self, flag_name: str) -> bool | None:
        """Get the specified feature flag; returns None if it does not exist. Will check
        that the HTTP response is correct and raise an AssertionError if not."""
        return self._get(ENDPOINTS.FEATURE, flag_name)

    def get_feature_flag_list(self) -> list[str]:
        """Get the specified feature flag; returns None if it does not exist. Will check
        that the HTTP response is correct and raise an AssertionError if not."""
        return self._get(ENDPOINTS.FEATURE)

    def best_effort_get_feature_flag(self, flag_name: str, fallback: T = None) -> bool | T:
        """Get the specified feature flag, returns fallback value (default None) if it
        doesn't exist or if there is a connection error - in the latter case logs
        to error."""
        try:
            return self._get(ENDPOINTS.FEATURE, flag_name)
        except (AssertionError, OSError):
            self._log.error(
                "Encountered an error reading from the config service.", exc_info=True
            )
            return fallback
