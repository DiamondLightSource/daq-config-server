import subprocess
import sys
from unittest.mock import MagicMock, patch

from daq_config_server.__main__ import (
    INSUFFICIENT_DEPENDENCIES_MESSAGE,
    __version__,
    main,
)


def test_cli_version():
    cmd = [sys.executable, "-m", "daq_config_server", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__


@patch("daq_config_server.app.main")
@patch("daq_config_server.__main__.print")
@patch("daq_config_server.__main__.ArgumentParser.parse_args")
@patch.dict("sys.modules", {"uvicorn": None, "fastapi": None})
def test_print_and_exit_if_incorrect_dependencies(
    mock_parse_args, mock_print: MagicMock, mock_main: MagicMock
):
    main()
    mock_print.assert_called_once_with(INSUFFICIENT_DEPENDENCIES_MESSAGE)
    mock_main.assert_not_called()


@patch("daq_config_server.app.main")
@patch("daq_config_server.__main__.ArgumentParser.parse_args")
def test_main_runs_with_correct_dependencies(mock_parse_args, mock_main: MagicMock):
    main()
    mock_main.assert_called_once()
