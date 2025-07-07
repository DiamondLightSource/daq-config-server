import json
import os
from typing import Any
from unittest.mock import MagicMock

import pytest
import requests

from daq_config_server.client import ConfigServer
from tests.constants import (
    ServerFilePaths,
    TestDataPaths,
)

SERVER_ADDRESS = "http://0.0.0.0:8555"

# Docs for running these system tests will be added in https://github.com/DiamondLightSource/daq-config-server/issues/68


@pytest.fixture
def server():
    return ConfigServer(SERVER_ADDRESS)


@pytest.mark.requires_local_server
def test_read_unformatted_file_as_plain_text(server: ConfigServer):
    with open(TestDataPaths.TEST_BEAMLINE_PARAMETERS_PATH) as f:
        expected_response = f.read()

    assert (
        server.get_file_contents(
            ServerFilePaths.BEAMLINE_PARAMETERS,
        )
        == expected_response
    )


@pytest.mark.requires_local_server
def test_read_file_as_bytes(server: ConfigServer):
    with open(TestDataPaths.TEST_BEAMLINE_PARAMETERS_PATH, "rb") as f:
        expected_response = f.read()

    assert (
        server.get_file_contents(
            ServerFilePaths.BEAMLINE_PARAMETERS,
            bytes,
        )
        == expected_response
    )


@pytest.mark.requires_local_server
def test_read_good_json_as_dict(server: ConfigServer):
    with open(TestDataPaths.TEST_GOOD_JSON_PATH) as f:
        expected_response = json.loads(f.read())

    assert (
        server.get_file_contents(
            ServerFilePaths.GOOD_JSON_FILE,
            dict[Any, Any],
        )
        == expected_response
    )


@pytest.mark.requires_local_server
def test_bad_json_gives_http_error_with_details(server: ConfigServer):
    file_path = ServerFilePaths.BAD_JSON_FILE
    file_name = os.path.basename(file_path)
    expected_detail = (
        f"Failed to convert {file_name} to application/json. "
        "Try requesting this file as a different type."
    )

    server._log.error = MagicMock()
    with pytest.raises(requests.exceptions.HTTPError):
        server.get_file_contents(
            file_path,
            dict[Any, Any],
        )
    server._log.error.assert_called_once_with(expected_detail)


@pytest.mark.requires_local_server
def test_request_with_file_not_on_whitelist(server: ConfigServer):
    file_path = "/not_allowed_file_location"
    with pytest.raises(
        requests.exceptions.HTTPError, match=f"{file_path} is not a whitelisted file."
    ):
        server.get_file_contents(
            file_path,
        )
