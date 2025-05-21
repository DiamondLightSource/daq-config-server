import json
from enum import StrEnum
from logging import Logger, getLogger
from typing import Any, TypeVar

import requests

from daq_config_server.app import AcceptedFileTypes

from .constants import ENDPOINTS

T = TypeVar("T")
BlParamDType = str | int | float | bool


class RequestedResponseFormats(StrEnum):
    DICT = AcceptedFileTypes.JSON  # Tries to convert to dict using json.loads()
    DECODED_STRING = AcceptedFileTypes.PLAIN_TEXT  # Use utf-8 decoding in response
    RAW_BYTE_STRING = AcceptedFileTypes.RAW_BYTES  # Use raw bytes in response


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
                case AcceptedFileTypes.JSON:
                    content = json.loads(r.content)
                case AcceptedFileTypes.PLAIN_TEXT:
                    content = r.text
                case _:
                    content = r.content
        except Exception:
            # TODO warn here
            content = r.content

        return content

    def get_file_contents(
        self,
        file_path: str,
        requested_response_format: RequestedResponseFormats = (
            RequestedResponseFormats.DECODED_STRING
        ),
    ) -> Any:
        headers = {"Accept": requested_response_format}
        return self._get(ENDPOINTS.CONFIG, headers, file_path)
