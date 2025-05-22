from unittest.mock import MagicMock, patch

from fastapi import status
from httpx import Response

from daq_config_server.client import ConfigServer
from daq_config_server.constants import ENDPOINTS


# More useful tests for the client are in tests/system_tests
@patch("daq_config_server.client.requests.get")
def test_read_unformatted_file(mock_request: MagicMock):
    mock_request.return_value = Response(status_code=status.HTTP_200_OK, json="test")
    file_path = "test"
    url = "url"
    server = ConfigServer(url)
    server.read_unformatted_file(file_path)
    mock_request.assert_called_once_with(url + ENDPOINTS.CONFIG + "/" + file_path)
