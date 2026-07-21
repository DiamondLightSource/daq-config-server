import json
from logging import Logger
from pathlib import Path
from typing import Any, Protocol

import requests
from requests import Response as RealResponse
from requests.exceptions import HTTPError

from daq_config_server.app.constants import ValidAcceptHeaders
from daq_config_server.models.base_model import ConfigModel

NonModel = str | bytes | dict[str, Any]
PathToMockDataDict = dict[str, ConfigModel | NonModel]


class MockResponse:
    """Lightweight stand-in for requests.Response used in unit tests.

    This class emulates the minimal interface of a real HTTP response
    required by ConfigClient, without performing any network operations.

    This allows tests to simulate server responses at different encoding
    layers (JSON, plain text, or raw bytes) while keeping behaviour
    consistent with real requests.Response objects.
    """

    def __init__(
        self,
        body: str | bytes,
        content_type: ValidAcceptHeaders,
    ):
        self.headers = {"content-type": content_type}
        self._body = body

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
    """Interface for retrieving configuration data from either a real server or a local
    mock implementation.
    """

    def get_response(
        self, endpoint: str, accept_header: ValidAcceptHeaders, file_path: Path
    ) -> ResponseType: ...


class MockServerResponse(ServerResponse):
    """Mock implementation of ServerResponse used for unit testing.

    This class simulates a config server by reading local files instead of performing
    HTTP requests. Supports optional overrides for a specified path to the data you
    want to return instead.
    """

    def __init__(self, path_to_mock_data: PathToMockDataDict | None = None):
        self.path_to_mock_data = path_to_mock_data or {}

    def get_response(
        self, endpoint: str, accept_header: ValidAcceptHeaders, file_path: Path
    ) -> MockResponse:
        if str(file_path) in self.path_to_mock_data:
            mock_data = self.path_to_mock_data[str(file_path)]
            if isinstance(mock_data, ConfigModel):
                mock_response = mock_data.model_dump_json()
            elif isinstance(mock_data, dict):
                mock_response = json.dumps(mock_data)
            elif isinstance(mock_data, bytes):
                mock_response = mock_data.decode()
            else:
                mock_response = mock_data
        else:
            mock_response = file_path.read_text()
        return MockResponse(mock_response, accept_header)


class RealServerResponse(ServerResponse):
    """Real HTTP implementation of ServerResponse used in production.

    This class communicates with a remote configuration server via HTTP
    requests and retrieves file contents from a deployed service.
    """

    def __init__(self, url: str, log: Logger):
        self._url = url
        self._log = log

    def get_response(
        self, endpoint: str, accept_header: ValidAcceptHeaders, file_path: Path
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
