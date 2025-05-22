import operator
from logging import Logger, getLogger
from typing import Any

import requests
from cachetools import TTLCache, cachedmethod

from .constants import ENDPOINTS


class ConfigServer:
    def __init__(
        self,
        url: str,
        log: Logger | None = None,
        cache_size: int = 10,
        cache_lifetime_s: int = 3600,
    ) -> None:
        """
        Initialize the ConfigServer client.

        Args:
            url: Base URL of the config server.
            log: Optional logger instance.
            cache_size: Size of the cache (maximum number of items can be stored).
            cache_lifetime_s: Lifetime of the cache (in seconds).
        """
        self._url = url.rstrip("/")
        self._log = log if log else getLogger("daq_config_server.client")
        self._cache = TTLCache(maxsize=cache_size, ttl=cache_lifetime_s)

    def _get(
        self,
        endpoint: str,
        item: str | None = None,
        reset_cached_result: bool = False,
    ) -> Any:
        """
        Get data from the config server with cache management.
        If a cached response doesn't already exist, makes a request to
        the config server.
        If reset_cached_result is true, remove the cache entry for that request and
        make a new request

        Args:
            endpoint: API endpoint.
            item: Optional item identifier.
            reset_cached_result: Whether to reset cache.

        Returns:
            The response data.
        """

        if (endpoint, item) in self._cache and reset_cached_result:
            del self._cache[(endpoint, item)]
        return self._cached_get(endpoint, item)

    @cachedmethod(cache=operator.attrgetter("_cache"))
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
            data = r.json()
            self._log.debug(f"Cache set for {endpoint}/{item}.")
            return data
        except requests.exceptions.HTTPError as e:
            self._log.error(f"HTTP error: {e}")
            raise

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
