import pytest
from tests.constants import TEST_DATA_DIR

from daq_config_server.client import ConfigServer

SERVER_ADDRESS = "http://0.0.0.0:8555"

"""For now, these tests require locally hosting the config server

While in the python environment, run

python -m daq_config_server --dev

before running the tests
"""


@pytest.fixture
def server():
    return ConfigServer(SERVER_ADDRESS)


def test_read_unformatted_file(server: ConfigServer):
    file_path = f"{TEST_DATA_DIR}/beamline_parameters.txt"
    with open(file_path) as f:
        expected_response = f.read()
    print("hing")
    assert (
        server.read_unformatted_file(f"{TEST_DATA_DIR}/beamline_parameters.txt")
        == expected_response
    )
