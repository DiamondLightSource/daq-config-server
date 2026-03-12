import json
from collections.abc import Callable
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import xmltodict
from fastapi import status
from fastapi.responses import JSONResponse, Response
from fastapi.testclient import TestClient

from daq_config_server.app._routes import (
    ENDPOINTS,
    ConverterParseError,
    ValidAcceptHeaders,
    get_converted_file_contents,
)
from daq_config_server.app.api import app
from daq_config_server.models.beamline_parameters import beamline_parameters_to_dict
from daq_config_server.models.lookup_tables import GenericLookupTable
from tests.constants import TestDataPaths


def test_get_converted_file_contents_uses_converter_if_file_in_map(
    mock_file_converter_map: dict[str, Callable[[str], Any]],
):
    file_to_convert = TestDataPaths.TEST_GOOD_XML_PATH
    mock_convert_function = MagicMock()
    mock_file_converter_map[str(file_to_convert)] = mock_convert_function
    get_converted_file_contents(file_to_convert)

    mock_convert_function.assert_called_once()


def test_get_converted_file_contents_converts_pydantic_model_to_dict(
    mock_file_converter_map: dict[str, Callable[[str], Any]],
):
    file_to_convert = TestDataPaths.TEST_GOOD_LUT_PATH
    model = GenericLookupTable(
        column_names=["column1", "column2"], rows=[[1, 2], [2, 3]]
    )
    mock_convert_function = MagicMock(return_value=model)
    mock_file_converter_map[str(file_to_convert)] = mock_convert_function
    result = get_converted_file_contents(file_to_convert)
    assert isinstance(result, dict)
    mock_convert_function.assert_called_once()


def test_error_is_raised_if_file_cant_be_parsed(
    mock_file_converter_map: dict[str, Callable[[str], Any]],
):
    file_to_convert = TestDataPaths.TEST_BAD_BEAMLINE_PARAMETERS_PATH
    mock_file_converter_map[str(file_to_convert)] = beamline_parameters_to_dict
    with pytest.raises(ConverterParseError):
        get_converted_file_contents(file_to_convert)


def test_xml_to_dict_gives_expected_result_and_can_be_jsonified():
    with open(TestDataPaths.TEST_GOOD_XML_PATH) as f:
        contents = f.read()
    expected = {
        "JCameraManSettings": {
            "levels": {
                "zoomLevel": [
                    {
                        "level": "1.0",
                        "micronsPerXPixel": "2.432",
                        "micronsPerYPixel": "2.432",
                        "position": "0",
                    },
                    {
                        "level": "1.5",
                        "micronsPerXPixel": "1.888",
                        "micronsPerYPixel": "1.888",
                        "position": "16.3",
                    },
                ],
            },
            "tolerance": "1.0",
        },
    }
    result = xmltodict.parse(contents)
    assert result == expected
    json.dumps(result)


@pytest.fixture
def mock_app():
    return TestClient(app)


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


@patch("daq_config_server.app._routes.path_is_whitelisted")
async def test_get_configuration_gives_http_422_on_failed_conversion(
    mock_validate: MagicMock, mock_app: TestClient, tmpdir: Path
):
    file_path = Path(f"{tmpdir}/test_bad_utf_8.txt")
    with open(file_path, "wb") as f:
        f.write(b"\x80\x81\xfe\xff")
    response = mock_app.get(
        f"{ENDPOINTS.CONFIG}/{file_path}", headers=ACCEPT_HEADER_DEFAULT
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_get_configuration_on_non_absolute_filepath(mock_app: TestClient):
    file_path = "relative_path"
    response = mock_app.get(f"{ENDPOINTS.CONFIG}/{file_path}")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


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
