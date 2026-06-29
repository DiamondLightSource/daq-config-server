import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pydantic
import pytest
import requests
from fastapi import status
from httpx import Response

from daq_config_server.app._routes import EndPoints, ValidAcceptHeaders
from daq_config_server.client._client import (
    ConfigClient,
    TModel,
    TNonModel,
    TypeConversionError,
    _get_mime_type,
)
from daq_config_server.models import ConfigModel, DisplayConfig
from daq_config_server.models.lookup_tables import (
    BeamlinePitchLookupTable,
    GenericLookupTable,
)
from daq_config_server.models.lookup_tables.insertion_device import (
    UndulatorEnergyGapLookupTable,
)
from daq_config_server.testing import make_test_response

REQUEST_PATCH = "daq_config_server.client._server_response.requests.get"

test_path = Path("test")


@pytest.fixture
def client() -> ConfigClient:
    return ConfigClient("url")


@patch(REQUEST_PATCH)
def test_config_client_get_file_contents_default_header(
    mock_request: MagicMock, client: ConfigClient
):
    mock_request.return_value = Response(
        status_code=status.HTTP_200_OK,
        content="test",
    )
    mock_request.return_value = make_test_response("test")
    assert client.get_file_contents(test_path) == "test"
    mock_request.assert_called_once_with(
        client._url + EndPoints.CONFIG + "/" + str(test_path),
        headers={"Accept": ValidAcceptHeaders.PLAIN_TEXT},
    )


@patch(REQUEST_PATCH)
def test_config_client_get_file_contents_with_bytes(
    mock_request: MagicMock, client: ConfigClient
):
    test_str = "test"
    mock_request.return_value = make_test_response(
        test_str, content_type=ValidAcceptHeaders.RAW_BYTES
    )
    assert (
        client.get_file_contents(test_path, desired_return_type=bytes)
        == test_str.encode()
    )


@patch(REQUEST_PATCH)
def test_config_client_get_file_contents_gives_exception_on_invalid_json(
    mock_request: MagicMock, client: ConfigClient
):
    content_type = ValidAcceptHeaders.JSON
    bad_json = "bad_dict}"
    mock_request.return_value = make_test_response(
        bad_json, content_type=content_type, json_value=bad_json
    )
    with pytest.raises(TypeConversionError):
        client.get_file_contents(test_path, desired_return_type=dict[Any, Any])


@patch(REQUEST_PATCH)
def test_config_client_get_file_contents_caching(
    mock_request: MagicMock, client: ConfigClient
):
    """Test reset_cached_result=False and reset_cached_result=True."""
    mock_request.side_effect = [
        make_test_response("1st_read"),
        make_test_response("2nd_read"),
        make_test_response("3rd_read"),
    ]
    assert client.get_file_contents(test_path, reset_cached_result=True) == "1st_read"
    assert client.get_file_contents(test_path, reset_cached_result=True) == "2nd_read"
    assert client.get_file_contents(test_path, reset_cached_result=False) == "2nd_read"


@patch(REQUEST_PATCH)
def test_config_client_bad_responses_no_details_raises_error(
    mock_request: MagicMock, client: ConfigClient
):
    """Test that a non-200 response raises a RequestException."""
    mock_request.return_value = make_test_response(
        "1st_read", status.HTTP_204_NO_CONTENT, raise_exc=requests.exceptions.HTTPError
    )
    client._log.error = MagicMock()
    with pytest.raises(requests.exceptions.HTTPError):
        client.get_file_contents(test_path)
    client._log.error.assert_called_once_with(
        "Response raised HTTP error but no details provided"
    )


@patch(REQUEST_PATCH)
def test_config_client_bad_responses_with_details_raises_error(
    mock_request: MagicMock, client: ConfigClient
):
    """Test that a non-200 response raises a RequestException."""

    detail = "test detail"
    mock_request.return_value = make_test_response(
        "1st_read",
        status.HTTP_204_NO_CONTENT,
        raise_exc=requests.exceptions.HTTPError,
        json_value="test",
    )
    mock_request.return_value.json = MagicMock(return_value={"detail": detail})
    client._log.error = MagicMock()
    with pytest.raises(requests.exceptions.HTTPError):
        client.get_file_contents(test_path)
    client._log.error.assert_called_once_with(detail)


@patch(REQUEST_PATCH)
def test_config_client_get_file_contents_with_untyped_dict(
    mock_request: MagicMock, client: ConfigClient
):
    content_type = ValidAcceptHeaders.JSON
    good_json = '{"good_dict":"test"}'
    mock_request.return_value = make_test_response(
        good_json, content_type=content_type, json_value=good_json
    )
    assert client.get_file_contents(test_path, desired_return_type=dict) == {
        "good_dict": "test"
    }


@pytest.mark.parametrize(
    "input, expected",
    [
        (dict, ValidAcceptHeaders.JSON),
        (dict[str, bytes], ValidAcceptHeaders.JSON),
        (dict[Any, Any], ValidAcceptHeaders.JSON),
        (str, ValidAcceptHeaders.PLAIN_TEXT),
        (bytes, ValidAcceptHeaders.RAW_BYTES),
        (GenericLookupTable, ValidAcceptHeaders.JSON),
        (DisplayConfig, ValidAcceptHeaders.JSON),
    ],
)
def test_get_mime_type(input: type[TModel | TNonModel], expected: ValidAcceptHeaders):
    assert _get_mime_type(input) == expected


@patch(REQUEST_PATCH)
def test_config_client_get_file_contents_with_force_parser_requests_str_from_server_and_converts(  # noqa: E501
    mock_request: MagicMock, client: ConfigClient
):
    mock_config = "mock_config"
    mock_request.return_value = make_test_response(mock_config)

    mock_converted_result = {"value": 12345}

    mock_converter = MagicMock(return_value=mock_converted_result)

    result = client.get_file_contents(test_path, dict, force_parser=mock_converter)

    mock_converter.assert_called_once_with(mock_config)
    mock_request.assert_called_once_with(
        "url/config/test", headers={"Accept": ValidAcceptHeaders.PLAIN_TEXT}
    )

    assert result == mock_converted_result


@pytest.mark.parametrize(
    "desired_return_type, expected_exception",
    [
        (UndulatorEnergyGapLookupTable, None),
        (BeamlinePitchLookupTable, pydantic.ValidationError),
    ],
)
@patch(REQUEST_PATCH)
def test_config_client_get_file_contents_with_force_parser_still_validates_desired_return_type(  # noqa: E501
    mock_request: MagicMock,
    client: ConfigClient,
    desired_return_type: type[ConfigModel],
    expected_exception: type[Exception] | None,
):
    mock_config = "Units eV mm\n5700		5.4606\n#24500		7.2\n"
    expected_result = UndulatorEnergyGapLookupTable(rows=[[5700, 5.4606]])
    mock_request.return_value = make_test_response(mock_config)

    if expected_exception:
        with pytest.raises(expected_exception):
            client.get_file_contents(
                test_path,
                desired_return_type,
                force_parser=UndulatorEnergyGapLookupTable.from_contents,
            )
    else:
        result = client.get_file_contents(
            test_path,
            desired_return_type,
            force_parser=UndulatorEnergyGapLookupTable.from_contents,
        )
        assert result == expected_result


@patch(REQUEST_PATCH)
def test_config_client_get_file_contents_with_bad_force_parser_errors(
    mock_request: MagicMock, client: ConfigClient
):
    mock_config = "Units eV mm\n5700		5.4606\n#24500		7.2\n"
    mock_request.return_value = make_test_response(mock_config)

    with pytest.raises(ValueError):
        client.get_file_contents(
            test_path,
            DisplayConfig,
            force_parser=DisplayConfig.from_contents,
        )


@patch(REQUEST_PATCH)
def test_reset_cache(mock_request: MagicMock):
    mock_config = "Units eV mm\n5700		5.4606\n#24500		7.2\n"
    mock_request.return_value = make_test_response(mock_config)
    server = ConfigClient("url")
    result = server.get_file_contents(test_path, str)

    assert server._cache.currsize == 1
    server.reset_cache()
    assert server._cache.currsize == 0

    new_mock_config = "Units eV mm\n6800		5.4606\n#24500		7.2\n"
    mock_request.return_value = make_test_response(new_mock_config)
    new_result = server.get_file_contents(
        test_path,
        str,
    )
    assert result != new_result


def test_mock_config_client_get_file_contents_as_dict_gives_expected_result(
    tmp_path: Path,
):
    file = tmp_path / "beamline.json"

    expected_data = {"x": 1, "y": "test"}
    file.write_text(json.dumps(expected_data))

    client = ConfigClient()
    client.configure_mock()

    result = client.get_file_contents(file, desired_return_type=dict)
    assert result == expected_data


def test_mock_config_client_get_file_contents_as_str_gives_expected_result(
    tmp_path: Path,
):
    file = tmp_path / "beamline.json"

    expected_data = '{"x": 1, "y": "test"}'
    file.write_text(expected_data)

    client = ConfigClient()
    client.configure_mock()

    result = client.get_file_contents(file)
    assert result == expected_data


class MyModel(ConfigModel):
    x: float = 1.5
    y: str = "test"
    z: list[int] = [1, 4, 5]


def test_mock_config_client_get_file_contents_as_config_model_gives_expected_result(
    tmp_path: Path,
):
    file = tmp_path / "beamline.json"
    expected_data = MyModel().model_dump_json()
    file.write_text(expected_data)

    client = ConfigClient()
    client.configure_mock()

    result = client.get_file_contents(file)
    assert result == expected_data


def test_mock_config_client_converter_table_to_json(tmp_path: Path):
    file = tmp_path / "beamline.txt"

    # "table" format (header + row)
    file.write_text("x|y\n1|test")

    def table_to_dict(contents: str) -> dict[str, Any]:
        lines = contents.strip().splitlines()
        headers = lines[0].split("|")
        values = lines[1].split("|")
        return dict(zip(headers, values, strict=True))

    client = ConfigClient()
    client.configure_mock({file: table_to_dict})

    result = client.get_file_contents(file, desired_return_type=dict)
    assert result == {"x": "1", "y": "test"}
