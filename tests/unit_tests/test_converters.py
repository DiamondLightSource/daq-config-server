from pathlib import Path

import pytest
from src.daq_config_server.converters import (
    _parse_lut_to_dict,
    display_config_to_dict,
    get_converted_file_contents,
)

from daq_config_server.converters import FILE_TO_CONVERTER_MAP
from tests.constants import (
    TestDataPaths,
)


def test_all_files_in_dict_can_be_parsed_with_no_errors():
    for filename in FILE_TO_CONVERTER_MAP.keys():
        get_converted_file_contents(Path(filename))


def test_parse_lut_to_dict_gives_expected_result():
    with open(TestDataPaths.TEST_GOOD_LUT_PATH) as f:
        contents = f.read()
    expected = {
        "units": {
            "energy": "eV",
            "gap": "mm",
        },
        "data": [
            {
                "energy": 5700,
                "gap": 5.4606,
            },
            {
                "energy": 5760,
                "gap": 5.5,
            },
            {
                "energy": 6000,
                "gap": 5.681,
            },
            {
                "energy": 6500,
                "gap": 6.045,
            },
        ],
    }
    assert (
        _parse_lut_to_dict(contents, ("energy", "eV", int), ("gap", "mm", float))
        == expected
    )


def test_parsing_bad_lut_causes_error():
    with open(TestDataPaths.TEST_BAD_LUT_PATH) as f:
        contents = f.read()
    with pytest.raises(IndexError):
        _parse_lut_to_dict(contents, ("energy", "eV", int), ("gap", "mm", float))


def test_display_config_to_dict_gives_expected_result():
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
    assert display_config_to_dict(contents) == expected
