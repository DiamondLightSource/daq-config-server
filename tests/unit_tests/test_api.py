import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from daq_config_server import app
from daq_config_server.app import AcceptedFileTypes
from daq_config_server.constants import ENDPOINTS
from tests.constants import TEST_DATA_DIR


@pytest.fixture
def mock_app():
    return TestClient(app.app)


HEADER_DEFAULTS = {"Accept": AcceptedFileTypes.PLAIN_TEXT}


async def _assert_get_and_response(
    client: TestClient,
    endpoint: str,
    expected_response: Any,
    header: dict = HEADER_DEFAULTS,
):
    response = client.get(endpoint, headers=header)
    assert response.status_code == status.HTTP_200_OK

    content_bytes = await response.aread()

    # Copy logic of the real client when decoding responses
    try:
        match header["Accept"]:
            case AcceptedFileTypes.JSON:
                content = response.json()
            case AcceptedFileTypes.PLAIN_TEXT:
                content = content_bytes.decode()
            case _:
                content = content_bytes
    except Exception:
        content = content_bytes

    assert content == expected_response


async def test_get_configuration_on_plain_text_file(mock_app: TestClient):
    file_path = f"{TEST_DATA_DIR}/beamline_parameters.txt"
    with open(file_path) as f:
        expected_response = f.read()
    await _assert_get_and_response(
        mock_app, f"{ENDPOINTS.CONFIG}/{file_path}", expected_response
    )


def test_get_configuration_exception_on_invalid_file(mock_app: TestClient):
    file_path = f"{TEST_DATA_DIR}/nonexistent_file.yaml"

    with pytest.raises(FileNotFoundError):
        mock_app.get(f"{ENDPOINTS.CONFIG}/{file_path}", headers=HEADER_DEFAULTS)


async def test_get_configuration_on_json_file(mock_app: TestClient):
    file_path = f"{TEST_DATA_DIR}/test_good_json.json"
    with open(file_path) as f:
        expected_response = json.load(f)
    await _assert_get_and_response(
        mock_app,
        f"{ENDPOINTS.CONFIG}/{file_path}",
        expected_response,
        header={"Accept": AcceptedFileTypes.JSON},
    )


@patch("daq_config_server.app.LOGGER.warning")
async def test_get_configuration_warns_and_uses_raw_bytes_on_invalid_json(
    mock_warn: MagicMock,
    mock_app: TestClient,
):
    file_path = f"{TEST_DATA_DIR}/test_bad_json"
    with open(file_path, "rb") as f:
        expected_response = f.read()
    await _assert_get_and_response(
        mock_app,
        f"{ENDPOINTS.CONFIG}/{file_path}",
        expected_response,
        header={"Accept": AcceptedFileTypes.JSON},
    )
    mock_warn.assert_called_once()
