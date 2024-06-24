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
        self._uri_prefix = self._url.request_uri if self._url.request_uri != "/" else ""
        if self._url.scheme != "http" and self._url.scheme != "https":
            raise ValueError("ConfigServer must use HTTP or HTTPS!")
        self._Conn = HTTPSConnection if self._url.scheme == "https" else HTTPConnection
        self._log = log if log else getLogger("daq_config_server.client")

    def _get(
        self,
        endpoint: str,
        item: str | None = None,
        options: dict[str, str] | None = None,
    ):
        req_item = f"/{item}" if item else ""
        conn = self._Conn(self._url.host, self._url.port or self._url.scheme)
        req_ops = (
            f"?{''.join(f'{k}={v}&' for k,v in options.items())}"[:-1]
            if options
            else ""
        )
        complete_req = self._uri_prefix + endpoint + req_item + req_ops
        conn.connect()
        conn.request("GET", complete_req )
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

    def get_all_feature_flags(self) -> dict | None:
        """Get the values for all flags; returns None if it does not exist. Will check
        that the HTTP response is correct and raise an AssertionError if not."""
        return self._get(ENDPOINTS.FEATURE, options={"get_values": "true"})

    def get_feature_flag_list(self) -> list[str]:
        """Get the list of all feature flags. Will check that the HTTP response is
        correct and raise an AssertionError if not."""
        return self._get(ENDPOINTS.FEATURE)

    def best_effort_get_feature_flag(
        self, flag_name: str, fallback: T = None
    ) -> bool | T:
        """Get the specified feature flag, returns fallback value (default None) if it
        doesn't exist or if there is a connection error - in the latter case logs to
        error."""
        try:
            return self._get(ENDPOINTS.FEATURE, flag_name)
        except (AssertionError, OSError):
            self._log.error(
                "Encountered an error reading from the config service.", exc_info=True
            )
            return fallback

    def best_effort_get_all_feature_flags(self) -> dict[str, bool]:
        """Get all flags, returns an empty dict if there are no flags, or if there
        is a connection error - in the latter case logs to error."""
        try:
            return self._get(ENDPOINTS.FEATURE, options={"get_values": "true"})
        except (AssertionError, OSError):
            self._log.error(
                "Encountered an error reading from the config service.", exc_info=True
            )
            return {}
