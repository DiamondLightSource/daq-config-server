import json
from enum import StrEnum
from logging import Logger, getLogger
from typing import Any, TypeVar

import requests

from daq_config_server.app import ValidAcceptHeaders

from .constants import ENDPOINTS

T = TypeVar("T")
BlParamDType = str | int | float | bool


class RequestedResponseFormats(StrEnum):
    DICT = ValidAcceptHeaders.JSON  # Convert to dict using json.loads()
    DECODED_STRING = ValidAcceptHeaders.PLAIN_TEXT  # Use utf-8 decoding in response
    RAW_BYTE_STRING = ValidAcceptHeaders.RAW_BYTES  # Use raw bytes in response


class ConfigServer:
    def __init__(self, url: str, log: Logger | None = None) -> None:
        self._url = url.rstrip("/")
        self._log = log if log else getLogger("daq_config_server.client")

    def _get(
        self,
        endpoint: str,
        headers: dict,
        item: str | None = None,
    ):
        r = requests.get(
            self._url + endpoint + (f"/{item}" if item else ""), headers=headers
        )

        content_type = r.headers["content-type"].split(";")[0].strip()

        try:
            match content_type:
                case ValidAcceptHeaders.JSON:
                    content = json.loads(r.content)
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
        file_path: str,
        requested_response_format: RequestedResponseFormats = (
            RequestedResponseFormats.DECODED_STRING
        ),
    ) -> Any:
        """
        Get an file contents from the config server in the format specified.

        If data parsing fails, the return type will be bytes

        Args:
            file_path: Path to the file.
            requested_response_format: Specify how to parse the response.
        Returns:
            The file contents, in the type specified.
        """
        headers = {"Accept": requested_response_format}
        return self._get(ENDPOINTS.CONFIG, headers, file_path)
