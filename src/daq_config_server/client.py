import operator
from collections import defaultdict
from logging import Logger, getLogger
from pathlib import Path
from typing import Any, TypeVar

import requests
from cachetools import TTLCache, cachedmethod
from pydantic import TypeAdapter
from requests import Response
from requests.exceptions import HTTPError

from daq_config_server.app import ValidAcceptHeaders

from .constants import ENDPOINTS

T = TypeVar("T", str, bytes, dict[Any, Any])


return_type_to_mime_type: dict[type, ValidAcceptHeaders] = defaultdict(
    lambda: ValidAcceptHeaders.PLAIN_TEXT,
    {
        dict[Any, Any]: ValidAcceptHeaders.JSON,
        str: ValidAcceptHeaders.PLAIN_TEXT,
        bytes: ValidAcceptHeaders.RAW_BYTES,
    },
)


class TypeConversionException(Exception): ...


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
        self._cache: TTLCache[tuple[str, str, Path], Response] = TTLCache(
            maxsize=cache_size, ttl=cache_lifetime_s
        )

    @cachedmethod(cache=operator.attrgetter("_cache"))
    def _cached_get(
        self,
        endpoint: str,
        accept_header: ValidAcceptHeaders,
        file_path: Path,
    ) -> Response:
        """
        Get data from the config server and cache it.

        Args:
            endpoint: API endpoint.
            accept_header: Accept header MIME type
            file_path: absolute path to the file which will be read

        Returns:
            The response data.
        """

        request_url = self._url + endpoint + (f"/{file_path}")
        r = requests.get(request_url, headers={"Accept": accept_header})
        # Intercept http exceptions from server so that the client
        # can include the response `detail` sent by the server
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            try:
                error_detail = r.json().get("detail")
                self._log.error(error_detail)
                raise HTTPError(error_detail) from err
            except ValueError:
                self._log.error("Response raised HTTP error but no details provided")
                raise HTTPError from err

        self._log.debug(f"Cache set for {request_url}.")
        return r

    def _get(
        self,
        endpoint: str,
        accept_header: ValidAcceptHeaders,
        file_path: Path,
        reset_cached_result: bool = False,
    ):
        """
        Get data from the config server with cache management and use
        the content-type response header to format the return value.
        If data parsing fails, return the response contents in bytes
        """
        if (
            endpoint,
            accept_header,
            file_path,
        ) in self._cache and reset_cached_result:
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
            raise TypeConversionException(
                f"Failed trying to convert to content-type {content_type}."
            ) from e

        return content

    def get_file_contents(
        self,
        file_path: Path | str,
        desired_return_type: type[T] = str,
        reset_cached_result: bool = False,
    ) -> T:
        """
        Get contents of a file from the config server in the format specified.
        Optionally look for cached result before making request.

        Current supported return types are: str, bytes, dict[str, str]. This option will
        determine how the server attempts to decode the file

        Args:
            file_path: Path to the file.
            requested_response_format: Specify how to parse the response.
            desired_return_type: If true, make a request and store response in cache,
                                otherwise look for cached response before making
                                new request
        Returns:
            The file contents, in the format specified.
        """
        file_path = Path(file_path)
        accept_header = return_type_to_mime_type[desired_return_type]

        return TypeAdapter(desired_return_type).validate_python(  # type: ignore - to allow any dict
            self._get(
                ENDPOINTS.CONFIG,
                accept_header,
                file_path,
                reset_cached_result=reset_cached_result,
            )
        )
