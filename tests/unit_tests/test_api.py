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
from tests.constants import TestDataPaths


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
    file_path = TestDataPaths.TEST_BEAMLINE_PARAMETERS_PATH
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
    file_path = TestDataPaths.TEST_BEAMLINE_PARAMETERS_PATH
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
    file_path = TestDataPaths.TEST_INVALID_FILE_PATH
    response = mock_app.get(
        f"{ENDPOINTS.CONFIG}/{file_path}", headers=ACCEPT_HEADER_DEFAULT
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


async def test_get_configuration_on_json_file(mock_app: TestClient):
    file_path = TestDataPaths.TEST_GOOD_JSON_PATH
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


@patch("daq_config_server.app.path_is_whitelisted")
async def test_get_configuration_gives_http_422_on_failed_conversion(
    mock_validate: MagicMock, mock_app: TestClient, tmpdir: Path
):
    file_path = Path(f"{tmpdir}/test_bad_utf_8.txt")
    with open(file_path, "wb") as f:
        f.write(b"\x80\x81\xfe\xff")
    response = mock_app.get(
        f"{ENDPOINTS.CONFIG}/{file_path}", headers=ACCEPT_HEADER_DEFAULT
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_health_check_returns_code_200(
    mock_app: TestClient,
):
    assert mock_app.get(ENDPOINTS.HEALTH).status_code == status.HTTP_200_OK


def test_validate_path_against_whitelist_on_valid_file(mock_app: TestClient):
    file_path = TestDataPaths.TEST_BEAMLINE_PARAMETERS_PATH
    response = mock_app.get(f"{ENDPOINTS.CONFIG}/{file_path}")
    assert response.status_code == status.HTTP_200_OK


def test_validate_path_against_whitelist_on_invalid_file(mock_app: TestClient):
    file_path = TestDataPaths.TEST_FILE_NOT_ON_WHITELIST_PATH
    response = mock_app.get(f"{ENDPOINTS.CONFIG}/{file_path}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_validate_path_against_whitelist_on_file_in_invalid_dir(mock_app: TestClient):
    file_path = TestDataPaths.TEST_FILE_IN_BAD_DIR
    response = mock_app.get(f"{ENDPOINTS.CONFIG}/{file_path}")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_validate_path_against_whitelist_on_file_in_valid_dir(mock_app: TestClient):
    file_path = TestDataPaths.TEST_FILE_IN_GOOD_DIR
    response = mock_app.get(f"{ENDPOINTS.CONFIG}/{file_path}")
    assert response.status_code == status.HTTP_200_OK


def test_get_configuration_on_non_absolute_filepath(mock_app: TestClient):
    file_path = "relative_path"
    response = mock_app.get(f"{ENDPOINTS.CONFIG}/{file_path}")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
