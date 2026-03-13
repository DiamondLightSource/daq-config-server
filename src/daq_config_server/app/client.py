import logging
import operator
from collections.abc import Callable
from logging import Logger, getLogger
from pathlib import Path
from threading import RLock
from typing import Any, TypeVar, get_origin, overload

import requests
from cachetools import TTLCache, cachedmethod
from pydantic import TypeAdapter
from requests import Response
from requests.exceptions import HTTPError

from daq_config_server.models.base_model import ConfigModel

from ._routes import ENDPOINTS, ValidAcceptHeaders

LOGGER = logging.getLogger(__name__)

TModel = TypeVar("TModel", bound=ConfigModel)
TNonModel = TypeVar("TNonModel", str, bytes, dict[str, Any])


class TypeConversionError(Exception): ...


def _get_mime_type(
    requested_return_type: type[TModel | TNonModel],
) -> ValidAcceptHeaders:
    # Get correct mapping for typed dict or plain dict
    if (
        get_origin(requested_return_type) is dict
        or requested_return_type is dict
        or issubclass(requested_return_type, ConfigModel)
    ):
        return ValidAcceptHeaders.JSON
    elif requested_return_type is bytes:
        return ValidAcceptHeaders.RAW_BYTES
    return ValidAcceptHeaders.PLAIN_TEXT


class ConfigClient:
    """Client to communicate with a deployed config service with a configurable cache
    and logger"""

    def __init__(
        self,
        url: str = "https://daq-config.diamond.ac.uk",
        log: Logger | None = None,
        cache_size: int = 10,
        cache_lifetime_s: int = 3600,
    ) -> None:
        """
        Args:
            url: Base URL of the config server. Defaults to central service.
            log: Optional logger instance.
            cache_size: Size of the cache (maximum number of items can be stored).
            cache_lifetime_s: Lifetime of the cache (in seconds).
        """
        self._url = url.rstrip("/")
        self._log = log if log else getLogger("daq_config_server.client")
        self._cache: TTLCache[tuple[str, str, Path], Response] = TTLCache(
            maxsize=cache_size, ttl=cache_lifetime_s
        )
        self._lock = RLock()

    @cachedmethod(
        cache=operator.attrgetter("_cache"), lock=operator.attrgetter("_lock")
    )
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
        cache_key = (endpoint, accept_header, file_path)
        if reset_cached_result:
            with self._lock:
                if cache_key in self._cache:
                    del self._cache[cache_key]

        r = self._cached_get(*cache_key)

        content_type = r.headers["content-type"].split(";")[0].strip()

        if content_type != accept_header:
            self._log.warning(
                f"Server failed to parse the file as requested. Requested "
                f"{accept_header} but response came as content-type {content_type}"
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
            raise TypeConversionError(
                f"Failed trying to convert to content-type {content_type}."
            ) from e

        return content

    def reset_cache(self):
        with self._lock:
            self._cache.clear()

    @overload
    def get_file_contents(
        self,
        file_path: str | Path,
        desired_return_type: type[TNonModel] = str,
        reset_cached_result: bool = False,
        force_parser: Callable[[str], Any] | None = None,
    ) -> TNonModel: ...

    @overload
    def get_file_contents(
        self,
        file_path: str | Path,
        desired_return_type: type[TModel],
        reset_cached_result: bool = False,
        force_parser: Callable[[str], Any] | None = None,
    ) -> TModel: ...

    def get_file_contents(
        self,
        file_path: str | Path,
        desired_return_type: type[Any] = str,
        reset_cached_result: bool = False,
        force_parser: Callable[[str], Any] | None = None,
    ) -> Any:
        """
        Get contents of a file from the config server in the format specified.
        Optionally look for cached result before making request.

        Current supported return types are: str, bytes, dict. This option will
        determine how the server attempts to decode the file. Note that only untyped
        dictionaries are currently supported

        Args:
            file_path: Path to the file.
            desired_return_type: Specify how to parse the response.
            reset_cached_result: If true, make a request and store response in cache,
                otherwise look for cached response before making new request
            force_parser: Optionally provide a function to convert the contents of a
                config file to the desired return type. This overides whatever converter
                is specified for that file in the FILE_TO_CONVERTER_MAP, and can be used
                if the config file isn't in the FILE_TO_CONVERTER_MAP at all. This
                should only be used for testing or when waiting on a release that will
                add the file to the FILE_TO_CONVERTER_MAP.
        Returns:
            The file contents, in the format specified.
        """
        file_path = Path(file_path)

        if force_parser:
            LOGGER.warning(
                "The force_parser argument should only be used for testing or "
                "as a temporary measure. Add your file and parser to the "
                "FILE_TO_CONVERTER_MAP. See "
                "https://github.com/DiamondLightSource/daq-config-server/blob/main/docs/how-to/config-server-guide.md#file-converters"
            )
            # force accept header to string so conversion is done client side
            accept_header = _get_mime_type(str)
        else:
            accept_header = _get_mime_type(desired_return_type)

        result = self._get(
            ENDPOINTS.CONFIG,
            accept_header,
            file_path,
            reset_cached_result=reset_cached_result,
        )
        if force_parser:
            assert isinstance(result, str)
            result = force_parser(result)

        return TypeAdapter(desired_return_type).validate_python(result)
