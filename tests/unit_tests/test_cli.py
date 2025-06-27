import subprocess
import sys
from unittest.mock import MagicMock, patch

from daq_config_server.__main__ import (
    INSUFFICIENT_DEPENDENCIES_MESSAGE,
    __version__,
    main,
)
from tests.constants import TEST_LOGGING_CONFIG_PATH


def test_cli_version():
    cmd = [sys.executable, "-m", "daq_config_server", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__


@patch("daq_config_server.app.main")
@patch("daq_config_server.__main__.print")
@patch("daq_config_server.__main__.ArgumentParser.parse_args")
@patch.dict("sys.modules", {"uvicorn": None, "fastapi": None})
def test_print_and_exit_if_incorrect_dependencies(
    mock_parse_args: MagicMock, mock_print: MagicMock, mock_main: MagicMock
):
    main()
    mock_print.assert_called_once_with(INSUFFICIENT_DEPENDENCIES_MESSAGE)
    mock_main.assert_not_called()


@patch("daq_config_server.app.main")
@patch("daq_config_server.__main__.ArgumentParser.parse_args")
def test_main_runs_with_correct_dependencies(
    mock_parse_args: MagicMock, mock_main: MagicMock
):
    main()
    mock_main.assert_called_once()


@patch("daq_config_server.app.main")
@patch("daq_config_server.__main__.ArgumentParser.parse_args")
@patch("daq_config_server.log.set_up_graylog_handler")
def test_logging_with_mounted_config(
    mock_graylog_setup: MagicMock, mock_parse_args: MagicMock, mock_main: MagicMock
):
    with patch("daq_config_server.__main__.CONFIG_PATH", new=TEST_LOGGING_CONFIG_PATH):
        main()
    mock_graylog_setup.assert_called_once()


@patch("daq_config_server.app.main")
@patch("daq_config_server.__main__.ArgumentParser.parse_args")
@patch("daq_config_server.log.set_up_graylog_handler")
def test_logging_with_no_mounted_config(
    mock_graylog_setup: MagicMock, mock_parse_args: MagicMock, mock_main: MagicMock
):
    # If config file doesn't exist, graylog option is disabled by default
    main()
    mock_graylog_setup.assert_not_called()
