import json
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock

import pytest
import xmltodict

from daq_config_server.converters._converter_utils import (
    ConverterParseError,
    parse_lut,
    parse_value,
    remove_comments,
)
from daq_config_server.converters._converters import (
    beamline_parameters_to_dict,
    beamline_pitch_lut,
    beamline_roll_lut,
    detector_xy_lut,
    display_config_to_model,
    undulator_energy_gap_lut,
)
from daq_config_server.converters.convert import get_converted_file_contents
from daq_config_server.converters.models import (
    DisplayConfig,
    DisplayConfigData,
    GenericLookupTable,
)
from tests.constants import (
    TestDataPaths,
)


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


def test_parse_lut_to_dict_gives_expected_result_and_can_be_jsonified():
    with open(TestDataPaths.TEST_GOOD_LUT_PATH) as f:
        contents = f.read()
    expected = GenericLookupTable(
        column_names=["energy_eV", "gap_mm"],
        rows=[[5700, 5.4606], [5760, 5.5], [6000, 5.681], [6500, 6.045]],
    )
    result = parse_lut(contents, ("energy_eV", int), ("gap_mm", float))
    assert result == expected
    result.model_dump_json()


def test_parsing_bad_lut_causes_error():
    with open(TestDataPaths.TEST_BAD_LUT_PATH) as f:
        contents = f.read()
    with pytest.raises(IndexError):
        parse_lut(contents, ("energy_eV", int), ("gap_mm", float))


def test_lut_with_different_number_of_row_items_to_column_names_causes_error():
    with pytest.raises(ValueError):
        GenericLookupTable(
            column_names=["column1", "column2"], rows=[[1, 2], [1, 2, 3]]
        )


def test_display_config_to_model_gives_expected_result_and_can_be_jsonified():
    with open(TestDataPaths.TEST_GOOD_DISPLAY_CONFIG_PATH) as f:
        contents = f.read()
    expected = DisplayConfig(
        zoom_levels={
            1.0: DisplayConfigData(
                bottomRightX=410,
                bottomRightY=278,
                crosshairX=541,
                crosshairY=409,
                topLeftX=383,
                topLeftY=253,
            ),
            2.5: DisplayConfigData(
                bottomRightX=388,
                bottomRightY=322,
                crosshairX=551,
                crosshairY=410,
                topLeftX=340,
                topLeftY=283,
            ),
        }
    )
    result = display_config_to_model(contents)
    assert result == expected
    json.dumps(result.model_dump())


def test_display_config_with_wrong_zoom_levels_causes_error():
    zoom_levels = {
        1.0: DisplayConfigData(
            bottomRightX=410,
            bottomRightY=278,
            crosshairX=541,
            crosshairY=409,
            topLeftX=383,
            topLeftY=253,
        ),
        2.5: DisplayConfigData(
            bottomRightX=388,
            bottomRightY=322,
            crosshairX=551,
            crosshairY=410,
            topLeftX=340,
            topLeftY=283,
        ),
    }
    with pytest.raises(ValueError):
        DisplayConfig(zoom_levels=zoom_levels, required_zoom_levels=({1.0, 3.0}))


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


def test_beamline_parameters_to_dict_gives_expected_result():
    with open(TestDataPaths.TEST_BEAMLINE_PARAMETERS_PATH) as f:
        contents = f.read()
    with open(TestDataPaths.EXPECTED_BEAMLINE_PARAMETERS_JSON_PATH) as f:
        expected = json.load(f)
    result = beamline_parameters_to_dict(contents)
    assert result == expected


def test_bad_beamline_parameters_with_non_keyword_string_value_causes_error():
    with open(TestDataPaths.TEST_BAD_BEAMLINE_PARAMETERS_PATH) as f:
        contents = f.read()
    with pytest.raises(ValueError):
        beamline_parameters_to_dict(contents)


def test_beam_line_parameters_with_repeated_key_causes_error():
    input = "thing = 1\nthing = 2"
    with pytest.raises(ValueError):
        beamline_parameters_to_dict(input)


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


def test_detector_xy_lut_gives_expected_results():
    input = (
        "# distance beamY beamX (values from mosflm)\n"
        "Units mm mm mm\n"
        "150 152.2 166.26\n"
        "800 152.08 160.96\n"
    )
    expected = GenericLookupTable(
        column_names=["detector_distances_mm", "beam_centre_x_mm", "beam_centre_y_mm"],
        rows=[[150, 152.2, 166.26], [800, 152.08, 160.96]],
    )
    result = detector_xy_lut(input)
    assert result == expected


def test_beamline_pitch_lut_gives_expected_result():
    input = (
        "#       Bragg	pitch\n"
        "#	Degree	values	for	pitch	are	interpreted	as	mrad\n"
        "#	The	values	cannot	change	direction.\n"
        "#       last update 2025/01/15 NP\n"
        "Units Deg mrad\n"
        "Units Deg Deg\n"
        "16.40956 -0.62681\n"
        "14.31123 -0.61833\n"
        "12.69285 -0.61243\n"
        "11.40557 -0.60849\n"
    )
    expected = GenericLookupTable(
        column_names=["bragg_angle_deg", "pitch_mrad"],
        rows=[
            [16.40956, -0.62681],
            [14.31123, -0.61833],
            [12.69285, -0.61243],
            [11.40557, -0.60849],
        ],
    )
    result = beamline_pitch_lut(input)
    assert result == expected


def test_beam_line_roll_lut_gives_expected_result():
    input = (
        "#Bragg angle against roll( absolute number)\n"
        "#reloadLookupTables()\n"
        "# last update 2024/06/20 NP\n"
        "Units Deg mrad\n"
        "26.4095 2.6154\n"
        "6.3075  2.6154\n"
    )
    expected = GenericLookupTable(
        column_names=["bragg_angle_deg", "roll_mrad"],
        rows=[[26.4095, 2.6154], [6.3075, 2.6154]],
    )
    result = beamline_roll_lut(input)
    assert result == expected


def test_undulator_gap_lut_gives_expected_result():
    input = (
        "#######################\n"
        "#                     #\n"
        "# 5.5mm CPMU 20/11/22 #\n"
        "#                     #\n"
        "Units eV mm\n"
        "5700		5.4606\n"
        "5760		5.5\n"
        "6000		5.681\n"
        "6500		6.045\n"
    )
    expected = GenericLookupTable(
        column_names=["energy_eV", "gap_mm"],
        rows=[[5700, 5.4606], [5760, 5.5], [6000, 5.681], [6500, 6.045]],
    )
    result = undulator_energy_gap_lut(input)
    assert result == expected
