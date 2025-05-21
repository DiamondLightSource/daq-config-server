from logging import Logger, getLogger
from typing import Any

import requests
from cachetools import TTLCache

from .constants import ENDPOINTS


class ConfigServer:
    def __init__(
        self,
        url: str,
        log: Logger | None = None,
        cache_size: int = 10,
        cache_lifetime: int = 3600,
    ) -> None:
        """
        Initialize the ConfigServer client.

        Args:
            url: Base URL of the config server.
            log: Optional logger instance.
        """
        self._url = url.rstrip("/")
        self._log = log if log else getLogger("daq_config_server.client")
        self._cache = TTLCache(maxsize=cache_size, ttl=cache_lifetime)

    def _get(
        self,
        endpoint: str,
        item: str | None = None,
        reset_cached_result: bool = False,
    ) -> Any:
        """
        Internal method to get data from the cache config server, with cache
        management.
        This method checks if the data is already cached. If it is, it returns
        the cached data. If not, it fetches the data from the config server,
        caches it, and returns the data.
        If reset_cached_result is True, it will remove the cached data and
        fetch it again from the config server.

        Args:
            endpoint: API endpoint.
            item: Optional item identifier.
            reset_cached_result: Whether to reset cache.

        Returns:
            The response data.
        """
        input_hash = hash(endpoint + (f"/{item}" if item else ""))
        if (input_hash) in self._cache:
            self._log.debug(f"Cache hit for {endpoint}/{item}.")

            if reset_cached_result:
                return self._cached_get(endpoint, item)
            return self._cache[input_hash]
        self._log.debug(f"Cache miss for {endpoint}/{item}.")
        return self._cached_get(endpoint, item)

    def _cached_get(
        self,
        endpoint: str,
        item: str | None = None,
    ) -> Any:
        """
        Get data from the config server and cache it.

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
            self._log.error(f"HTTP error: {e}")
            raise
        response = r.json()
        self._cache[hash(endpoint + (f"/{item}" if item else ""))] = r.json()
        self._log.debug(f"Cache set for {endpoint}/{item}.")
        return response

    def read_unformatted_file(
        self, file_path: str, reset_cached_result: bool = False
    ) -> Any:
        """
        Read an unformatted file from the config server.

        Args:
            file_path: Path to the file.
            reset_cached_result: Whether to reset cache.

        Returns:
            The file content.
        """
        return self._get(
            ENDPOINTS.CONFIG, file_path, reset_cached_result=reset_cached_result
        )
