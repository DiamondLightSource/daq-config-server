import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from daq_config_server.__main__ import __version__, main
from daq_config_server.app import main as main_app
from daq_config_server.app._config import WhitelistConfig
from daq_config_server.app.api import app, lifespan, log_request_details
from tests.constants import TEST_CONFIG_PATH


@pytest.fixture
def mock_app():
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_init_whitelist():
    with patch("daq_config_server.app.api.init_whitelist") as patched_fn:
        yield patched_fn


async def test_log_request_details():
    with patch("daq_config_server.app.api.LOGGER") as logger:
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


def test_cli_version():
    cmd = [sys.executable, "-m", "daq_config_server", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__


@patch("daq_config_server.app.api.uvicorn.run")
@patch("daq_config_server.app._log.set_up_graylog_handler")
def test_logging_with_mounted_config(
    mock_graylog_setup: MagicMock, mock_run: MagicMock
):
    with patch("daq_config_server.app._config.CONFIG_PATH", new=TEST_CONFIG_PATH):
        main_app()
    mock_graylog_setup.assert_called_once()


@patch("daq_config_server.__main__.main_app")
@patch("daq_config_server.__main__.ArgumentParser.parse_args")
def test_main(mock_parse_args: MagicMock, mock_main: MagicMock):
    main()
    mock_main.assert_called_once()


@patch("daq_config_server.app.api.uvicorn.run")
@patch("daq_config_server.app._log.set_up_graylog_handler")
def test_logging_with_no_mounted_config(
    mock_graylog_setup: MagicMock, mock_run: MagicMock
):
    # If config file doesn't exist, graylog option is disabled by default
    main_app()
    mock_graylog_setup.assert_not_called()


@patch("daq_config_server.app.api.get_whitelist")
@patch("daq_config_server.app.api.uvicorn.run")
async def test_app_lifespan_calls_init_whitelist(
    mock_run: MagicMock, mock_get_whitelist: MagicMock, mock_init_whitelist: MagicMock
):
    async with lifespan(MagicMock()):
        mock_init_whitelist.assert_called_once_with(WhitelistConfig())
    mock_get_whitelist.return_value.stop.assert_called_once()
