from unittest.mock import MagicMock, patch

import pytest
import requests
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


@patch("daq_config_server.client.requests.get")
def test_read_unformatted_file_reading_cache(mock_request: MagicMock):
    mock_request.side_effect = [
        Response(status_code=status.HTTP_200_OK, json="1st_read"),
        Response(status_code=status.HTTP_200_OK, json="2nd_read"),
        Response(status_code=status.HTTP_200_OK, json="3rd_read"),
    ]
    file_path = "test"
    url = "url"
    server = ConfigServer(url)
    assert "1st_read" == server.read_unformatted_file(file_path)

    assert "1st_read" == server.read_unformatted_file(file_path)
    assert "2nd_read" == server.read_unformatted_file(file_path, use_cache=False)
    assert "2nd_read" == server.read_unformatted_file(file_path)
    assert "3rd_read" == server.read_unformatted_file(file_path, use_cache=False)


@patch("daq_config_server.client.requests.get")
def test_read_unformatted_file_reading_not_OK(mock_request: MagicMock):
    mock_request.side_effect = [
        Response(status_code=status.HTTP_204_NO_CONTENT, json="1st_read"),
    ]
    file_path = "test"
    url = "url"
    server = ConfigServer(url)
    with pytest.raises(requests.RequestException):
        server.read_unformatted_file(file_path)
