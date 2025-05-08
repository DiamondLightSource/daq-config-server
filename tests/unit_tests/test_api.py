import json
from typing import Any

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from tests.constants import TEST_DATA_DIR

from daq_config_server import app
from daq_config_server.constants import ENDPOINTS


@pytest.fixture
def mock_app():
    return TestClient(app.app)


async def _assert_get_and_response(
    client: TestClient, endpoint: str, expected_response: Any
):
    response = client.get(endpoint)
    assert response.status_code == status.HTTP_200_OK
    content = json.loads(await response.aread())
    assert content == expected_response


async def test_get_configuration_on_valid_file(mock_app: TestClient):
    file_path = f"{TEST_DATA_DIR}/beamline_parameters.txt"
    with open(file_path) as f:
        expected_response = f.read()
    await _assert_get_and_response(
        mock_app, f"{ENDPOINTS.CONFIG}/{file_path}", expected_response
    )


def test_get_configuration_exception_on_invalid_file(mock_app: TestClient):
    file_path = f"{TEST_DATA_DIR}/nonexistent_file.yaml"
    with pytest.raises(FileNotFoundError):
        mock_app.get(f"{ENDPOINTS.CONFIG}/{file_path}")
