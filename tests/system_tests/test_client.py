import json
import os
from collections.abc import Callable
from typing import Any, get_type_hints
from unittest.mock import MagicMock, patch

import pytest
import requests
from pydantic import ValidationError

from daq_config_server.app._file_converter_map import (
    FILE_TO_CONVERTER_MAP,
)
from daq_config_server.app.client import ConfigClient
from daq_config_server.models import ConfigModel, DisplayConfig
from daq_config_server.models.lookup_tables import (
    BeamlinePitchLookupTable,
    BeamlineRollLookupTable,
)
from daq_config_server.models.lookup_tables.insertion_device import (
    UndulatorEnergyGapLookupTable,
)
from tests.constants import (
    ServerFilePaths,
    TestDataPaths,
)

SERVER_ADDRESS = "http://0.0.0.0:8555"
DEPLOYED_SERVER_ADDRESS = "https://daq-config.diamond.ac.uk"

# See docs for running these system tests: https://diamondlightsource.github.io/daq-config-server/main/index.html#testing


@pytest.fixture
def server():
    return ConfigClient(SERVER_ADDRESS)


@pytest.fixture
def deployed_server():
    return ConfigClient(DEPLOYED_SERVER_ADDRESS)


@pytest.mark.requires_local_server
def test_read_unformatted_file_as_plain_text(server: ConfigClient):
    with open(TestDataPaths.TEST_BEAMLINE_PARAMETERS_PATH) as f:
        expected_response = f.read()

    assert (
        server.get_file_contents(
            ServerFilePaths.BEAMLINE_PARAMETERS,
        )
        == expected_response
    )


@pytest.mark.requires_local_server
def test_read_file_as_bytes(server: ConfigClient):
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
def test_read_good_json_as_dict(server: ConfigClient):
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
def test_read_good_json_as_untyped_dict(server: ConfigClient):
    with open(TestDataPaths.TEST_GOOD_JSON_PATH) as f:
        expected_response = json.loads(f.read())

    assert (
        server.get_file_contents(
            ServerFilePaths.GOOD_JSON_FILE,
            dict,
        )
        == expected_response
    )


@pytest.mark.requires_local_server
def test_bad_json_gives_http_error_with_details(server: ConfigClient):
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
def test_request_with_file_not_on_whitelist(server: ConfigClient):
    file_path = "/not_allowed_file_location"
    with pytest.raises(
        requests.exceptions.HTTPError, match=f"{file_path} is not a whitelisted file."
    ):
        server.get_file_contents(
            file_path,
        )


@pytest.mark.requires_local_server
def test_request_for_file_with_converter_works(server: ConfigClient):
    expected = {
        "rows": [[5700, 5.4606], [5760, 5.5], [6000, 5.681], [6500, 6.045]],
    }
    result = server.get_file_contents(ServerFilePaths.GOOD_LUT, dict)
    assert result == expected


@pytest.mark.requires_local_server
def test_request_for_file_with_converter_works_with_pydantic_model(
    server: ConfigClient,
):
    expected = UndulatorEnergyGapLookupTable(
        rows=[[5700, 5.4606], [5760, 5.5], [6000, 5.681], [6500, 6.045]],
    )
    result = server.get_file_contents(
        ServerFilePaths.GOOD_LUT, UndulatorEnergyGapLookupTable
    )
    assert isinstance(result, UndulatorEnergyGapLookupTable)
    assert result == expected


@pytest.mark.requires_local_server
def test_request_for_file_with_converter_with_wrong_pydantic_model_errors(
    server: ConfigClient,
):
    with pytest.raises(ValidationError):
        server.get_file_contents(ServerFilePaths.GOOD_LUT, DisplayConfig)


@pytest.mark.parametrize(
    "file_converter_map_entry, desired_return_type, converter",
    [
        (
            UndulatorEnergyGapLookupTable,
            BeamlinePitchLookupTable,
            BeamlinePitchLookupTable.from_contents,
        ),
        (
            UndulatorEnergyGapLookupTable.from_contents,
            BeamlineRollLookupTable,
            BeamlineRollLookupTable.from_contents,
        ),
        (
            None,
            UndulatorEnergyGapLookupTable,
            UndulatorEnergyGapLookupTable.from_contents,
        ),
    ],
)
@pytest.mark.requires_local_server
def test_get_file_contents_with_force_parser_option_overides_converter_to_config_map(
    server: ConfigClient,
    mock_file_converter_map: dict[str, Callable[[str], Any]],
    file_converter_map_entry: Callable[[str], Any] | None,
    desired_return_type: type[ConfigModel],
    converter: Callable[[str], Any],
):
    filepath = ServerFilePaths.GOOD_LUT

    if file_converter_map_entry is None:
        del mock_file_converter_map[str(filepath)]
    else:
        mock_file_converter_map[str(filepath)] = file_converter_map_entry

    result = server.get_file_contents(
        filepath,
        desired_return_type,
        force_parser=converter,
    )
    assert isinstance(result, desired_return_type)


@pytest.mark.requires_deployed_server
def test_all_files_in_file_converter_map_can_be_converted_to_dict(
    deployed_server: ConfigClient,
):
    for filename in FILE_TO_CONVERTER_MAP.keys():
        if filename.startswith("/tests/test_data/"):
            continue
        result = deployed_server.get_file_contents(filename, dict)
        assert isinstance(result, dict)


@pytest.mark.requires_deployed_server
def test_all_files_in_file_converter_map_can_be_converted_to_target_type(
    deployed_server: ConfigClient,
):
    with patch(
        "daq_config_server.app._file_converter_map.xmltodict.parse.__annotations__",
        {"return": dict},  # Force a return type for xmltodict.parse()
    ):
        for filename, converter in FILE_TO_CONVERTER_MAP.items():
            if filename.startswith("/tests/test_data/"):
                continue
            return_type = get_type_hints(converter)["return"]
            assert return_type is dict or issubclass(return_type, ConfigModel)
            result = deployed_server.get_file_contents(filename, return_type)
            assert isinstance(result, return_type)
