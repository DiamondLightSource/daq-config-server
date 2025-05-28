import json

import pytest

from daq_config_server.client import ConfigServer, RequestedResponseFormats
from tests.constants import (
    TEST_BAD_JSON_PATH,
    TEST_BEAMLINE_PARAMETERS_PATH,
    TEST_GOOD_JSON_PATH,
)

SERVER_ADDRESS = "http://0.0.0.0:8555"

"""For now, these tests require locally hosting the config server

While in the python environment, run from the terminal:

daq-config-server

before running the tests
"""


@pytest.fixture
def server():
    return ConfigServer(SERVER_ADDRESS)


@pytest.mark.requires_local_server
def test_read_unformatted_file_as_plain_text(server: ConfigServer):
    file_path = TEST_BEAMLINE_PARAMETERS_PATH
    with open(file_path) as f:
        expected_response = f.read()

    assert (
        server.get_file_contents(
            file_path,
        )
        == expected_response
    )


@pytest.mark.requires_local_server
def test_read_file_as_bytes(server: ConfigServer):
    file_path = TEST_BEAMLINE_PARAMETERS_PATH
    with open(file_path, "rb") as f:
        expected_response = f.read()

    assert (
        server.get_file_contents(
            file_path,
            requested_response_format=RequestedResponseFormats.RAW_BYTE_STRING,
        )
        == expected_response
    )


@pytest.mark.requires_local_server
def test_read_good_json_as_dict(server: ConfigServer):
    file_path = TEST_GOOD_JSON_PATH
    with open(file_path) as f:
        expected_response = json.loads(f.read())

    assert (
        server.get_file_contents(
            file_path,
            requested_response_format=RequestedResponseFormats.DICT,
        )
        == expected_response
    )


@pytest.mark.requires_local_server
def test_bad_json_read_as_bytes(server: ConfigServer):
    file_path = TEST_BAD_JSON_PATH
    with open(file_path, "rb") as f:
        expected_response = f.read()

    assert (
        server.get_file_contents(
            file_path,
            requested_response_format=RequestedResponseFormats.DICT,
        )
        == expected_response
    )
