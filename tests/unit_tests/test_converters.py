import json
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock

import pytest

from daq_config_server.converters._converter_utils import (
    parse_lut_to_dict,
    parse_value,
    remove_comments,
)
from daq_config_server.converters._converters import (
    beamline_parameters_to_dict,
    display_config_to_dict,
    xml_to_dict,
)
from daq_config_server.converters.convert import get_converted_file_contents
from tests.constants import (
    TestDataPaths,
)


def test_get_converted_file_contents_uses_converter_if_file_in_map(
    mock_file_converter_map: dict[str, Callable[[str], Any]],
):
    file_to_convert = TestDataPaths.TEST_GOOD_XML_PATH
    mock_convert_function = MagicMock()
    mock_file_converter_map[str(TestDataPaths.TEST_GOOD_XML_PATH)] = (
        mock_convert_function
    )
    get_converted_file_contents(file_to_convert)

    mock_convert_function.assert_called_once()


def test_parse_lut_to_dict_gives_expected_result_and_can_be_jsonified():
    with open(TestDataPaths.TEST_GOOD_LUT_PATH) as f:
        contents = f.read()
    expected = {
        "column_names": ["energy_eV", "gap_mm"],
        "data": [[5700, 5.4606], [5760, 5.5], [6000, 5.681], [6500, 6.045]],
    }
    result = parse_lut_to_dict(contents, ("energy_eV", int), ("gap_mm", float))
    print(result)
    assert result == expected
    json.dumps(result)


def test_parsing_bad_lut_causes_error():
    with open(TestDataPaths.TEST_BAD_LUT_PATH) as f:
        contents = f.read()
    with pytest.raises(IndexError):
        parse_lut_to_dict(contents, ("energy_eV", int), ("gap_mm", float))


def test_display_config_to_dict_gives_expected_result_and_can_be_jsonified():
    with open(TestDataPaths.TEST_GOOD_DISPLAY_CONFIG_PATH) as f:
        contents = f.read()
    expected = {
        "1.0": {
            "bottomRightX": 410,
            "bottomRightY": 278,
            "crosshairX": 541,
            "crosshairY": 409,
            "topLeftX": 383,
            "topLeftY": 253,
        },
        "2.5": {
            "bottomRightX": 388,
            "bottomRightY": 322,
            "crosshairX": 551,
            "crosshairY": 410,
            "topLeftX": 340,
            "topLeftY": 283,
        },
    }
    result = display_config_to_dict(contents)
    assert result == expected
    json.dumps(result)


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
    result = xml_to_dict(contents)
    assert result == expected
    json.dumps(result)


def test_beamline_parameters_to_dict_gives_expected_result_and_can_be_jsonified():
    with open(TestDataPaths.TEST_BEAMLINE_PARAMETERS_PATH) as f:
        contents = f.read()
    with open(TestDataPaths.EXPECTED_BEAMLINE_PARAMETERS_JSON_PATH) as f:
        expected = json.load(f)
    result = beamline_parameters_to_dict(contents)
    assert result == expected


def test_bad_beamline_parameters_causes_error_to_be_raised():
    with open(TestDataPaths.TEST_BAD_BEAMLINE_PARAMETERS_PATH) as f:
        contents = f.read()
    with pytest.raises(ValueError):
        beamline_parameters_to_dict(contents)


def test_remove_comments_works_as_expected():
    input = [
        "This line should not be changed",
        "This should stay   # this should go",
        "#This entire line should go",
        "       # as should this one",
        "#        and this one",
        "",
        "  ",
        "   whitespace should be stripped    ",
    ]
    expected_output = [
        "This line should not be changed",
        "This should stay",
        "whitespace should be stripped",
    ]
    assert remove_comments(input) == expected_output


@pytest.mark.parametrize(
    "value, convert_to, expected_parsed_value",
    [
        ("  2.0   ", None, 2.0),
        (" 3 ", None, 3),
        ("5.0", float, 5.0),
        ("5", int, 5),
    ],
)
def test_parse_value_works_as_expected(
    value: str, convert_to: type, expected_parsed_value: Any
):
    parsed_value = parse_value(value, convert_to)
    assert parsed_value == expected_parsed_value
    assert type(parsed_value) is type(expected_parsed_value)
