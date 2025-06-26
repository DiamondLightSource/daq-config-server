from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import requests
from fastapi import status
from httpx import Response

from daq_config_server.app import ValidAcceptHeaders
from daq_config_server.client import ConfigServer, TypeConversionException
from daq_config_server.constants import ENDPOINTS
from daq_config_server.testing import make_test_response

test_path = Path("test")


@patch("daq_config_server.client.requests.get")
def test_get_file_contents_default_header(mock_request: MagicMock):
    mock_request.return_value = Response(
        status_code=status.HTTP_200_OK,
        content="test",
    )
    mock_request.return_value = make_test_response("test")
    url = "url"
    server = ConfigServer(url)
    assert server.get_file_contents(test_path) == "test"
    mock_request.assert_called_once_with(
        url + ENDPOINTS.CONFIG + "/" + str(test_path),
        headers={"Accept": ValidAcceptHeaders.PLAIN_TEXT},
    )


@patch("daq_config_server.client.requests.get")
def test_get_file_contents_with_bytes(mock_request: MagicMock):
    test_str = "test"
    mock_request.return_value = make_test_response(
        test_str, content_type=ValidAcceptHeaders.RAW_BYTES
    )
    url = "url"
    server = ConfigServer(url)
    assert (
        server.get_file_contents(test_path, desired_return_type=bytes)
        == test_str.encode()
    )


@patch("daq_config_server.client.requests.get")
def test_get_file_contents_gives_exception_on_invalid_json(
    mock_request: MagicMock,
):
    content_type = ValidAcceptHeaders.JSON
    bad_json = "bad_dict}"
    mock_request.return_value = make_test_response(
        bad_json, content_type=content_type, json_value=bad_json
    )
    url = "url"
    server = ConfigServer(url)
    with pytest.raises(TypeConversionException):
        server.get_file_contents(test_path, desired_return_type=dict[Any, Any])


@patch("daq_config_server.client.requests.get")
def test_get_file_contents_caching(
    mock_request: MagicMock,
):
    """Test reset_cached_result=False and reset_cached_result=True."""
    mock_request.side_effect = [
        make_test_response("1st_read"),
        make_test_response("2nd_read"),
        make_test_response("3rd_read"),
    ]
    url = "url"
    server = ConfigServer(url)
    assert server.get_file_contents(test_path, reset_cached_result=True) == "1st_read"
    assert server.get_file_contents(test_path, reset_cached_result=True) == "2nd_read"
    assert server.get_file_contents(test_path, reset_cached_result=False) == "2nd_read"


@patch("daq_config_server.client.requests.get")
def test_bad_responses_no_details_raises_error(mock_request: MagicMock):
    """Test that a non-200 response raises a RequestException."""
    mock_request.return_value = make_test_response(
        "1st_read", status.HTTP_204_NO_CONTENT, raise_exc=requests.exceptions.HTTPError
    )
    server = ConfigServer("url")
    server._log.error = MagicMock()
    with pytest.raises(requests.exceptions.HTTPError):
        server.get_file_contents(test_path)
    server._log.error.assert_called_once_with(
        "Response raised HTTP error but no details provided"
    )


@patch("daq_config_server.client.requests.get")
def test_bad_responses_with_details_raises_error(mock_request: MagicMock):
    """Test that a non-200 response raises a RequestException."""

    detail = "test detail"
    mock_request.return_value = make_test_response(
        "1st_read",
        status.HTTP_204_NO_CONTENT,
        raise_exc=requests.exceptions.HTTPError,
        json_value="test",
    )
    mock_request.return_value.json = MagicMock(return_value={"detail": detail})
    server = ConfigServer("url")
    server._log.error = MagicMock()
    with pytest.raises(requests.exceptions.HTTPError):
        server.get_file_contents(test_path)
    server._log.error.assert_called_once_with(detail)
