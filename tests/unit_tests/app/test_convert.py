import json
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock

import pytest
import xmltodict

from daq_config_server.app._convert import (
    ConverterParseError,
    get_converted_file_contents,
)
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
