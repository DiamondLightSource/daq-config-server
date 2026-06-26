import json
from collections.abc import Callable
from logging import Logger
from pathlib import Path
from typing import Any, Protocol

import requests
from requests import Response as RealResponse
from requests.exceptions import HTTPError

from daq_config_server.models.base_model import ConfigModel

from ._routes import ValidAcceptHeaders

ConverterDict = dict[Path, Callable[[str], Any]]


class MockResponse:
    def __init__(
        self,
        body: str | bytes,
        content_type: ValidAcceptHeaders,
        status_code: int = 200,
    ):
        self._body = body
        self.headers = {"content-type": content_type}
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError()

    def json(self) -> Any:
        """Match requests.Response: JSON is parsed from text/bytes."""
        if isinstance(self._body, bytes):
            return json.loads(self._body.decode())
        return json.loads(self._body)

    @property
    def text(self) -> str:
        if isinstance(self._body, bytes):
            return self._body.decode()
        return self._body

    @property
    def content(self) -> bytes:
        if isinstance(self._body, bytes):
            return self._body
        return self._body.encode()


ResponseType = RealResponse | MockResponse


class ServerResponse(Protocol):
    def get_response(
        self,
        endpoint: str,
        accept_header: ValidAcceptHeaders,
        file_path: Path,
    ) -> ResponseType: ...


class MockServerResponse(ServerResponse):
    def __init__(self, mock_data_converters: ConverterDict | None = None):
        self._mock_data_converters = mock_data_converters or {}

    def get_response(
        self,
        endpoint: str,
        accept_header: ValidAcceptHeaders,
        file_path: Path,
    ) -> MockResponse:
        raw = file_path.read_text()
        # Apply optional converter hook
        if file_path in self._mock_data_converters:
            converted = self._mock_data_converters[file_path](raw)
            # If it's a Pydantic model, serialize properly
            if isinstance(converted, ConfigModel):
                raw = converted.model_dump_json()

            elif isinstance(converted, dict):
                raw = json.dumps(converted)
            # otherwise assume already string-like
            else:
                raw = str(converted)
        return MockResponse(raw, accept_header)


class RealServerResponse(ServerResponse):
    def __init__(self, url: str, log: Logger):
        self._url = url
        self._log = log

    def get_response(
        self,
        endpoint: str,
        accept_header: ValidAcceptHeaders,
        file_path: Path,
    ) -> ResponseType:
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
        return r
