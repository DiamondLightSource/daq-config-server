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
        options: dict[str, str] | None = None,
        data: dict[str, Any] | None = None,
    ):
        r = requests.get(
            self._url + endpoint + (f"/{item}" if item else ""), options, json=data
        )
        return r.json()

    def get_beamline_param(self, param: str) -> BlParamDType | None:
        return self._get(ENDPOINTS.BL_PARAM, param).get(param)

    def get_some_beamline_params(self, params: list[str]) -> dict[str, BlParamDType]:
        return self._get(ENDPOINTS.BL_PARAM, data={"param_list": params})

    def get_all_beamline_params(self) -> dict[str, BlParamDType]:
        return self._get(ENDPOINTS.BL_PARAM)

    def get_feature_flag(self, flag_name: str) -> bool | None:
        """Get the specified feature flag; returns None if it does not exist. Will check
        that the HTTP response is correct and raise an AssertionError if not."""
        return self._get(ENDPOINTS.FEATURE, flag_name).get(flag_name)

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
            assert (
                result := self._get(ENDPOINTS.FEATURE, flag_name).get(flag_name)
            ) is not None
            return result
        except (AssertionError, OSError):
            self._log.error(
                "Encountered an error reading from the config service.", exc_info=True
            )
            return fallback

    def best_effort_get_all_feature_flags(self) -> dict[str, bool]:
        """Get all flags, returns an empty dict if there are no flags, or if there
        is a connection error - in the latter case logs to error."""
        try:
            assert (
                result := self._get(ENDPOINTS.FEATURE, options={"get_values": "true"})
            ) is not None
            return result
        except (AssertionError, OSError):
            self._log.error(
                "Encountered an error reading from the config service.", exc_info=True
            )
            return {}
