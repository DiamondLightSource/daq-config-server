import operator
from enum import StrEnum
from logging import Logger, getLogger
from pathlib import Path
from typing import Any

import requests
from cachetools import TTLCache, cachedmethod
from requests import Response

from daq_config_server.app import ValidAcceptHeaders

from .constants import ENDPOINTS


class RequestedResponseFormats(StrEnum):
    DICT = ValidAcceptHeaders.JSON  # Convert to dict using Response.json()
    DECODED_STRING = ValidAcceptHeaders.PLAIN_TEXT  # Use utf-8 decoding in response
    RAW_BYTE_STRING = ValidAcceptHeaders.RAW_BYTES  # Use raw bytes in response


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
        self._cache: TTLCache[tuple[str, str, Path], str] = TTLCache(
            maxsize=cache_size, ttl=cache_lifetime_s
        )

    @cachedmethod(cache=operator.attrgetter("_cache"))
    def _cached_get(
        self,
        endpoint: str,
        accept_header: str,
        file_path: Path,
    ) -> Response:
        """
        Get data from the config server and cache it.

        Args:
            endpoint: API endpoint.
            file_path: absolute path to the file which will be read

        Returns:
            The response data.
        """

        try:
            request_url = self._url + endpoint + (f"/{file_path}")
            r = requests.get(request_url, headers={"Accept": accept_header})
            r.raise_for_status()
            self._log.debug(f"Cache set for {request_url}.")
            return r
        except requests.exceptions.HTTPError as e:
            self._log.error(f"HTTP error: {e}")
            raise

    def _get(
        self,
        endpoint: str,
        accept_header: str,
        file_path: Path,
        reset_cached_result: bool = False,
    ):
        """
        Get data from the config server with cache management and use
        the content-type response header to format the return value.
        If data parsing fails, return the response contents in bytes
        """
        if (endpoint, accept_header, file_path) in self._cache and reset_cached_result:
            del self._cache[(endpoint, accept_header, file_path)]
        r = self._cached_get(endpoint, accept_header, file_path)

        content_type = r.headers["content-type"].split(";")[0].strip()

        if content_type != accept_header:
            self._log.warning(
                f"Server failed to parse the file as requested. Requested \
                {accept_header} but response came as content-type {content_type}"
            )

        try:
            match content_type:
                case ValidAcceptHeaders.JSON:
                    content = r.json()
                case ValidAcceptHeaders.PLAIN_TEXT:
                    content = r.text
                case _:
                    content = r.content
        except Exception as e:
            self._log.warning(
                f"Failed trying to convert to content-type {content_type} due to\
                exception {e} \nReturning as bytes instead"
            )
            content = r.content

        return content

    def get_file_contents(
        self,
        file_path: Path,
        requested_response_format: RequestedResponseFormats = (
            RequestedResponseFormats.DECODED_STRING
        ),
        reset_cached_result: bool = False,
    ) -> Any:
        """
        Get contents of a file from the config server in the format specified.
        If data parsing fails, contents will return as raw bytes. Optionally look
        for cached result before making request.

        Args:
            file_path: Path to the file.
            requested_response_format: Specify how to parse the response.
            reset_cached_result: If true, make a request and store response in cache,
                                otherwise look for cached response before making
                                new request
        Returns:
            The file contents, in the format specified.
        """

        return self._get(
            ENDPOINTS.CONFIG,
            requested_response_format,
            file_path,
            reset_cached_result=reset_cached_result,
        )
