from time import sleep
from unittest.mock import MagicMock, patch

import pytest
import requests
from fastapi import status

from daq_config_server.client import ConfigServer
from daq_config_server.constants import ENDPOINTS


def make_mock_response(json_value, status_code=200, raise_exc=None):
    mock_response = MagicMock()
    mock_response.json.return_value = json_value
    mock_response.status_code = status_code
    if raise_exc:
        mock_response.raise_for_status.side_effect = raise_exc
    else:
        mock_response.raise_for_status.return_value = None
    return mock_response


@patch("daq_config_server.client.requests.get")
def test_read_unformatted_file(mock_request: MagicMock):
    """Test that read_unformatted_file calls the correct endpoint and
    returns the expected result."""
    mock_request.return_value = make_mock_response({"key": "value"}, status.HTTP_200_OK)
    file_path = "test"
    url = "url"
    server = ConfigServer(url)
    result = server.read_unformatted_file(file_path)
    assert result == {"key": "value"}
    mock_request.assert_called_once_with(url + ENDPOINTS.CONFIG + "/" + file_path)


@patch("daq_config_server.client.requests.get")
def test_read_unformatted_file_reading_cache(mock_request: MagicMock):
    """Test cache behavior for read_unformatted_file."""
    mock_request.side_effect = [
        make_mock_response("1st_read", status.HTTP_200_OK),
        make_mock_response("2nd_read", status.HTTP_200_OK),
        make_mock_response("3rd_read", status.HTTP_200_OK),
    ]
    file_path = "test"
    url = "url"
    server = ConfigServer(url)
    assert server.read_unformatted_file(file_path) == "1st_read"
    assert server.read_unformatted_file(file_path) == "1st_read"  # Cached
    assert (
        server.read_unformatted_file(file_path, reset_cached_result=True) == "2nd_read"
    )
    assert server.read_unformatted_file(file_path) == "2nd_read"  # Cached
    assert (
        server.read_unformatted_file(file_path, reset_cached_result=True) == "3rd_read"
    )


@patch("daq_config_server.client.requests.get")
def test_read_unformatted_file_reading_reset_cached_result_true_without_cache(
    mock_request: MagicMock,
):
    """Test repeated reset_cached_result=False disables cache for each call."""
    mock_request.side_effect = [
        make_mock_response("1st_read", status.HTTP_200_OK),
    ]
    file_path = "test"
    url = "url"
    server = ConfigServer(url)
    assert (
        server.read_unformatted_file(file_path, reset_cached_result=True) == "1st_read"
    )


@patch("daq_config_server.client.requests.get")
def test_read_unformatted_file_reading_not_OK(mock_request: MagicMock):
    """Test that a non-200 response raises a RequestException."""
    mock_request.return_value = make_mock_response(
        "1st_read", status.HTTP_204_NO_CONTENT, raise_exc=requests.exceptions.HTTPError
    )
    file_path = "test"
    url = "url"
    server = ConfigServer(url)
    with pytest.raises(requests.exceptions.HTTPError):
        server.read_unformatted_file(file_path)


@patch("daq_config_server.client.requests.get")
def test_read_unformatted_file_reading_cache_custom_size(mock_request: MagicMock):
    mock_request.side_effect = [
        make_mock_response("1st_read", status.HTTP_200_OK),
        make_mock_response("2nd_read", status.HTTP_200_OK),
        make_mock_response("3rd_read", status.HTTP_200_OK),
    ]
    file_path = "test"
    url = "url"
    server = ConfigServer(url=url, cache_size=1)
    assert server.read_unformatted_file(file_path) == "1st_read"
    assert server.read_unformatted_file(file_path + "1") == "2nd_read"
    assert server.read_unformatted_file(file_path) == "3rd_read"


@patch("daq_config_server.client.requests.get")
def test_read_unformatted_file_cache_custom_lifetime(mock_request: MagicMock):
    mock_request.side_effect = [
        make_mock_response("1st_read", status.HTTP_200_OK),
        make_mock_response("2nd_read", status.HTTP_200_OK),
        make_mock_response("3rd_read", status.HTTP_200_OK),
    ]
    file_path = "test"
    url = "url"
    server = ConfigServer(url=url, cache_lifetime_s=0.1)  # type: ignore
    assert server.read_unformatted_file(file_path) == "1st_read"
    assert server.read_unformatted_file(file_path) == "1st_read"
    sleep(0.1)
    assert server.read_unformatted_file(file_path) == "2nd_read"
