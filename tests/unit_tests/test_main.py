import subprocess
import sys
from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from daq_config_server.__main__ import __version__, main
from daq_config_server.app import log_request_details
from daq_config_server.app import main as main_app
from tests.constants import TEST_CONFIG_PATH


def test_cli_version():
    cmd = [sys.executable, "-m", "daq_config_server", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__


@patch("daq_config_server.app.uvicorn.run")
@patch("daq_config_server.log.set_up_graylog_handler")
def test_logging_with_mounted_config(
    mock_graylog_setup: MagicMock, mock_run: MagicMock
):
    with patch("daq_config_server.app.CONFIG_PATH", new=TEST_CONFIG_PATH):
        main_app()
    mock_graylog_setup.assert_called_once()


@patch("daq_config_server.__main__.main_app")
@patch("daq_config_server.__main__.ArgumentParser.parse_args")
def test_main(mock_parse_args: MagicMock, mock_main: MagicMock):
    main()
    mock_main.assert_called_once()


@patch("daq_config_server.app.uvicorn.run")
@patch("daq_config_server.log.set_up_graylog_handler")
def test_logging_with_no_mounted_config(
    mock_graylog_setup: MagicMock, mock_run: MagicMock
):
    # If config file doesn't exist, graylog option is disabled by default
    main_app()
    mock_graylog_setup.assert_not_called()


async def test_log_request_details():
    with patch("daq_config_server.app.LOGGER") as logger:
        app = FastAPI()
        app.middleware("http")(log_request_details)

        @app.get("/")
        async def root():  # type: ignore
            return {"message": "Hello World"}

        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        logger.debug.assert_called_once_with(
            "method: GET url: http://testserver/ body: b''"
        )
