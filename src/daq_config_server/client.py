from logging import Logger, getLogger
from typing import Any, TypeVar

import requests
from cachetools import TTLCache, cached

from .constants import ENDPOINTS

T = TypeVar("T")
BlParamDType = str | int | float | bool
CACHE_SIZE = 10
CACHE_TTL = 3600  # seconds

# Cache for the config server
CACHE = TTLCache(maxsize=CACHE_SIZE, ttl=CACHE_TTL)


class ConfigServer:
    def __init__(self, url: str, log: Logger | None = None) -> None:
        """
        Initialize the ConfigServer client.

        Args:
            url: Base URL of the config server.
            log: Optional logger instance.
        """
        self._url = url.rstrip("/")
        self._log = log if log else getLogger("daq_config_server.client")

    def _get(
        self,
        endpoint: str,
        item: str | None = None,
        use_cache: bool = True,
    ) -> Any:
        """
        Internal method to get data from the config server, optionally using cache.

        Args:
            endpoint: API endpoint.
            item: Optional item identifier.
            use_cache: Whether to use the cache.

        Returns:
            The response data.
        """
        if not use_cache:
            if (self, endpoint, item) in CACHE:
                CACHE.pop((self, endpoint, item))
                self._log.debug(f"Cache entry for {endpoint}/{item} removed.")
        return self._cached_get(endpoint, item)

    @cached(cache=CACHE)
    def _cached_get(
        self,
        endpoint: str,
        item: str | None = None,
    ) -> Any:
        """
        Get a cached value from the config server.

        Args:
            endpoint: API endpoint.
            item: Optional item identifier.

        Returns:
            The response data.
        """
        url = self._url + endpoint + (f"/{item}" if item else "")

        try:
            r = requests.get(url)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return "Error: " + str(e)
        return r.json()

    def read_unformatted_file(self, file_path: str, use_cache: bool = True) -> Any:
        """
        Read an unformatted file from the config server.

        Args:
            file_path: Path to the file.
            use_cache: Whether to use the cache.

        Returns:
            The file content.
        """
        return self._get(ENDPOINTS.CONFIG, file_path, use_cache=use_cache)
