import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from daq_config_server.app.constants import ValidAcceptHeaders
from daq_config_server.client import ResponseProtocol, ServerResponse
from daq_config_server.models.base_model import ConfigModel

NonModel = str | bytes | dict[str, Any]
PathToMockDataDict = dict[str, ConfigModel | NonModel]


class MockResponse(ResponseProtocol):
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
        self._headers = {"content-type": content_type}
        self._body = body

    @property
    def headers(self) -> Mapping[str, ValidAcceptHeaders]:
        return self._headers

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


class MockServerResponse(ServerResponse):
    """Mock implementation of ServerResponse used for unit testing.

    This class simulates a config server by reading local files instead of performing
    HTTP requests. Supports optional overrides for a specified path to the data you
    want to return instead.
    """

    def __init__(self, path_to_mock_data: PathToMockDataDict | None = None):
        self.path_to_mock_data = path_to_mock_data or {}
        self.url = "mock-url"

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
