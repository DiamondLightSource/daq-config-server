import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.responses import JSONResponse, Response
from fastapi.testclient import TestClient

from daq_config_server import app
from daq_config_server.app import ValidAcceptHeaders
from daq_config_server.constants import ENDPOINTS
from tests.constants import (
    TEST_BEAMLINE_PARAMETERS_PATH,
    TEST_GOOD_JSON_PATH,
)


@pytest.fixture
def mock_app():
    return TestClient(app.app)


ACCEPT_HEADER_DEFAULT = {"Accept": ValidAcceptHeaders.PLAIN_TEXT}


async def _assert_get_and_response(
    client: TestClient,
    endpoint: str,
    expected_response: Response,
    accept_header: dict[str, ValidAcceptHeaders] = ACCEPT_HEADER_DEFAULT,
):
    response = client.get(endpoint, headers=accept_header)
    assert response.status_code == expected_response.status_code
    assert response.content == expected_response.body
    # Real content type includes encoding, eg 'text/plain; charset=utf-8'.
    # Just check the first part here.
    assert (
        response.headers["content-type"].split(";")[0].strip()
        == expected_response.headers["content-type"]
    )


async def test_get_configuration_on_plain_text_file(mock_app: TestClient):
    file_path = TEST_BEAMLINE_PARAMETERS_PATH
    with open(file_path) as f:
        expected_contents = f.read()

    expected_type = ValidAcceptHeaders.PLAIN_TEXT

    expected_response = Response(
        content=expected_contents,
        headers={"content-type": expected_type},
        status_code=status.HTTP_200_OK,
    )

    await _assert_get_and_response(
        mock_app, f"{ENDPOINTS.CONFIG}/{file_path}", expected_response
    )


async def test_get_configuration_raw_bytes(mock_app: TestClient):
    file_path = TEST_BEAMLINE_PARAMETERS_PATH
    with open(file_path, "rb") as f:
        expected_contents = f.read()
    expected_type = ValidAcceptHeaders.RAW_BYTES
    expected_response = Response(
        content=expected_contents,
        headers={"content-type": expected_type},
        status_code=status.HTTP_200_OK,
    )

    await _assert_get_and_response(
        mock_app,
        f"{ENDPOINTS.CONFIG}/{file_path}",
        expected_response,
        accept_header={"Accept": expected_type},
    )


def test_get_configuration_exception_on_invalid_file(mock_app: TestClient):
    file_path = Path("/nonexistent_file.yaml")
    response = mock_app.get(
        f"{ENDPOINTS.CONFIG}/{file_path}", headers=ACCEPT_HEADER_DEFAULT
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_configuration_on_json_file(mock_app: TestClient):
    file_path = TEST_GOOD_JSON_PATH
    with open(file_path) as f:
        expected_contents = json.load(f)
    expected_type = ValidAcceptHeaders.JSON
    expected_response = JSONResponse(
        content=expected_contents,
        headers={"content-type": expected_type},
        status_code=status.HTTP_200_OK,
    )
    await _assert_get_and_response(
        mock_app,
        f"{ENDPOINTS.CONFIG}/{file_path}",
        expected_response,
        accept_header={"Accept": expected_type},
    )


@patch("daq_config_server.app.LOGGER.warning")
async def test_get_configuration_warns_and_uses_raw_bytes_on_failed_utf_8_encoding(
    mock_warn: MagicMock, mock_app: TestClient, tmpdir: Path
):
    file_path = Path(f"{tmpdir}/test_bad_utf_8.txt")
    with open(file_path, "wb") as f:
        f.write(b"\x80\x81\xfe\xff")
    expected_contents = b"\x80\x81\xfe\xff"
    expected_type = ValidAcceptHeaders.RAW_BYTES
    expected_response = Response(
        content=expected_contents,
        headers={"content-type": expected_type},
        status_code=status.HTTP_200_OK,
    )
    await _assert_get_and_response(
        mock_app,
        f"{ENDPOINTS.CONFIG}/{file_path}",
        expected_response,
        accept_header={"Accept": ValidAcceptHeaders.PLAIN_TEXT},
    )
    mock_warn.assert_called_once()


async def test_health_check_returns_code_200(
    mock_app: TestClient,
):
    assert mock_app.get(ENDPOINTS.HEALTH).status_code == status.HTTP_200_OK
