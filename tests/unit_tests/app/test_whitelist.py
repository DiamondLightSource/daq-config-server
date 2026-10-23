import threading
from collections.abc import Generator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from _pytest.fixtures import FixtureRequest

from daq_config_server.app._config import WhitelistConfig
from daq_config_server.app._whitelist import (
    FilesystemWhitelist,
    get_whitelist,
    init_whitelist,
)

"""The tests in this file will read directly from the whitelist.yaml in the current
branch"""

LEGACY_SHARED_WHITELIST = Path(__file__).resolve().parents[3] / "whitelist.yaml"
DEFAULT_WHITELIST = (
    Path(__file__).resolve().parents[3] / "helm/daq-config-server/whitelist.yaml"
)


@pytest.fixture()
def mock_log_info():
    with patch("daq_config_server.app._whitelist.LOGGER.info") as mock_fn:
        yield mock_fn


@pytest.fixture()
def inject_whitelist(
    request: FixtureRequest, mock_log_info: MagicMock
) -> Generator[None, None, None]:
    with (
        patch("daq_config_server.app._whitelist.Thread"),
        patch("daq_config_server.app._whitelist.FilesystemWhitelist.stop"),
    ):
        init_whitelist(WhitelistConfig(config_file=str(request.param)))
        yield


@pytest.mark.parametrize("inject_whitelist", [LEGACY_SHARED_WHITELIST], indirect=True)
def test_legacy_whitelist_contains_expected_data(inject_whitelist: None):
    whitelist = get_whitelist()
    expected_files = {
        Path("/tests/test_data/beamline_parameters.txt"),
    }
    expected_dirs = {
        Path("/tests/test_data/"),
        Path("/dls_sw/i04/software/daq_configuration/"),
    }
    assert expected_files.issubset(whitelist.whitelist_files)
    assert expected_dirs.issubset(whitelist.whitelist_dirs)


@pytest.mark.parametrize("inject_whitelist", [DEFAULT_WHITELIST], indirect=True)
def test_default_whitelist_contains_expected_data(inject_whitelist: None):
    whitelist = get_whitelist()
    expected_files = {
        Path("/tests/test_data/beamline_parameters.txt"),
    }
    expected_dirs = {
        Path("/tests/test_data/"),
    }
    assert expected_files.issubset(whitelist.whitelist_files)
    assert expected_dirs.issubset(whitelist.whitelist_dirs)


@pytest.mark.parametrize("inject_whitelist", [DEFAULT_WHITELIST], indirect=True)
def test_initial_load_on_successful_fetch(
    mock_log_info: MagicMock,
    inject_whitelist: None,
):
    mock_log_info.assert_called_once_with("Successfully read whitelist.")


@patch("daq_config_server.app._whitelist.LOGGER.error")
def test_initial_load_on_failed_fetch(mock_log_error: MagicMock):
    with patch.object(
        FilesystemWhitelist, "_fetch_and_update", side_effect=Exception("blah")
    ):
        # Expect a RuntimeError because _initial_load wraps _fetch_and_update failures
        with pytest.raises(
            RuntimeError, match="Failed to load whitelist during initialization."
        ):
            FilesystemWhitelist(DEFAULT_WHITELIST)

    mock_log_error.assert_called_once_with("Initial whitelist load failed: blah")


@patch("daq_config_server.app._whitelist.WHITELIST_REFRESH_RATE_S", new=0)
@patch("daq_config_server.app._whitelist.LOGGER.error")
def test_periodically_update_whitelist_on_failed_update(mock_log_error: MagicMock):
    with patch.object(FilesystemWhitelist, "_initial_load"):
        with patch.object(
            FilesystemWhitelist,
            "_fetch_and_update",
            side_effect=Exception("blah"),
        ):
            whitelist = FilesystemWhitelist(Path("/test/path"))

            # Stop the thread immediately to prevent looping
            whitelist.stop()

            # Call periodic method directly (single iteration)
            whitelist._periodically_update_whitelist()

            mock_log_error.assert_called_with("Failed to update whitelist: blah")


@patch("daq_config_server.app._whitelist.LOGGER")
@patch("daq_config_server.app._whitelist.WHITELIST_REFRESH_RATE_S", new=0)
def test_periodically_update_whitelist_on_successful_update(
    mock_log: MagicMock,
):
    logging_event = threading.Event()

    def complete_logging_event_on_current_message(msg: str):
        if msg == "Whitelist updated successfully.":
            logging_event.set()

    mock_log.info.side_effect = complete_logging_event_on_current_message
    whitelist = FilesystemWhitelist(DEFAULT_WHITELIST)
    try:
        assert logging_event.wait(timeout=0.1)
        mock_log.error.assert_not_called()
    finally:
        whitelist.stop()


def test_file_based_whitelist():
    whitelist_path = "tests/test_data/whitelist.yaml"
    config = WhitelistConfig(config_file=whitelist_path)
    init_whitelist(config)
    whitelist = get_whitelist()
    assert whitelist.whitelist_files == {
        Path("/tests/test_data/beamline_parameters.txt")
    }
    assert whitelist.whitelist_dirs == {Path("/tests/test_data/good_dir")}
