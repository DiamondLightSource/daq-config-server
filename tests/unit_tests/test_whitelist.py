import threading
from pathlib import Path
from time import sleep
from unittest.mock import MagicMock, patch

import pytest

from daq_config_server.whitelist import WhitelistFetcher, get_whitelist

"""The tests in this file will read directly from the whitelist.yaml in the current
branch"""


def test_fetch_and_update_contructs_whitelist_given_yaml():
    whitelist = get_whitelist()
    expected_files = {
        Path("/tests/test_data/beamline_parameters.txt"),
    }
    expected_dirs = {
        Path("/tests/test_data/"),
        Path("/dls_sw/i03/software/daq_configuration/"),
    }
    assert expected_files.issubset(whitelist.whitelist_files)
    assert expected_dirs.issubset(whitelist.whitelist_dirs)


@patch("daq_config_server.whitelist.LOGGER.info")
def test_initial_load_on_sucessful_fetch(mock_log_info: MagicMock):
    get_whitelist()
    mock_log_info.assert_called_once_with("Successfully read whitelist from GitHub.")


@patch("daq_config_server.whitelist.LOGGER.error")
def test_initial_load_on_failed_fetch(mock_log_error: MagicMock):
    WhitelistFetcher._fetch_and_update = MagicMock(side_effect=Exception("blah"))
    with pytest.raises(RuntimeError):
        get_whitelist()
    mock_log_error.assert_called_once_with("Initial whitelist load failed: blah")


@pytest.mark.use_threading
@patch("daq_config_server.whitelist.LOGGER.error")
@patch("daq_config_server.whitelist.WHITELIST_REFRESH_RATE_S", new=0)
def test_periodically_update_whitelist_on_failed_update(mock_log_error: MagicMock):
    WhitelistFetcher._initial_load = MagicMock()
    WhitelistFetcher._fetch_and_update = MagicMock(side_effect=Exception("blah"))
    get_whitelist()
    sleep(0.01)
    mock_log_error.assert_called_with("Failed to update whitelist: blah")


@pytest.mark.use_threading
@patch("daq_config_server.whitelist.LOGGER")
@patch("daq_config_server.whitelist.WHITELIST_REFRESH_RATE_S", new=0)
def test_periodically_update_whitelist_on_successful_update(mock_log: MagicMock):
    logging_event = threading.Event()
    WhitelistFetcher._initial_load = MagicMock()
    WhitelistFetcher._fetch_and_update = MagicMock()

    def complete_logging_event_on_current_message(msg: str):
        if msg == "Whitelist updated successfully.":
            logging_event.set()

    mock_log.info.side_effect = complete_logging_event_on_current_message
    get_whitelist()
    assert logging_event.wait(timeout=0.1)
    mock_log.error.assert_not_called()
