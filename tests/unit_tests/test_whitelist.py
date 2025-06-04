# TODO system tests which actually try to make the request
from pathlib import Path
from time import sleep
from unittest.mock import MagicMock, patch

import pytest

from daq_config_server.testing import make_test_response
from daq_config_server.whitelist import Whitelist, get_whitelist

FAKE_WHITELIST_RESPONSE = """\
whitelist_files:
  - /test/file1.txt
  - /test/file2.txt
whitelist_dirs:
  - /test/dir1
  - /test/dir2
"""


@patch("daq_config_server.whitelist.requests.get")
def test_fetch_and_update_contructs_whitelist_given_yaml_response(
    mock_request: MagicMock,
):
    mock_request.return_value = make_test_response(content=FAKE_WHITELIST_RESPONSE)
    whitelist = get_whitelist()
    expected_files = {Path("/test/file1.txt"), Path("/test/file2.txt")}
    expected_dirs = {Path("/test/dir1"), Path("/test/dir2")}
    assert whitelist.whitelist_files == expected_files
    assert whitelist.whitelist_dirs == expected_dirs


@patch("daq_config_server.whitelist.LOGGER.info")
@patch("daq_config_server.whitelist.requests.get")
def test_initial_load_on_sucessful_fetch(
    mock_request: MagicMock, mock_log_info: MagicMock
):
    mock_request.return_value = make_test_response(content=FAKE_WHITELIST_RESPONSE)
    get_whitelist()
    mock_log_info.assert_called_once_with("Successfully read whitelist from GitHub.")


@patch("daq_config_server.whitelist.LOGGER.error")
@patch("daq_config_server.whitelist.requests.get")
def test_initial_load_on_failed_fetch(
    mock_request: MagicMock, mock_log_error: MagicMock
):
    Whitelist._fetch_and_update = MagicMock(side_effect=Exception("blah"))
    with pytest.raises(RuntimeError):
        get_whitelist()
    mock_log_error.assert_called_once_with("Initial whitelist load failed: blah")


@patch("daq_config_server.whitelist.LOGGER.error")
@patch("daq_config_server.whitelist.WHITELIST_REFRESH_RATE_S", new=0)
@patch("daq_config_server.whitelist.requests.get")
def test_periodically_update_whitelist_on_failed_update(
    mock_request: MagicMock, mock_log_error: MagicMock
):
    Whitelist._initial_load = MagicMock()
    Whitelist._fetch_and_update = MagicMock(side_effect=Exception("blah"))
    get_whitelist()
    sleep(0.01)
    mock_log_error.assert_called_with("Failed to update whitelist: blah")


@patch("daq_config_server.whitelist.LOGGER")
@patch("daq_config_server.whitelist.WHITELIST_REFRESH_RATE_S", new=0)
@patch("daq_config_server.whitelist.requests.get")
def test_periodically_update_whitelist_on_successful_update(
    mock_request: MagicMock, mock_log: MagicMock
):
    Whitelist._initial_load = MagicMock()
    Whitelist._fetch_and_update = MagicMock()
    get_whitelist()
    sleep(0.01)
    mock_log.error.assert_not_called()
    mock_log.info.assert_called_with("Whitelist updated successfully.")
