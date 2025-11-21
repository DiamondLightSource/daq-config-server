from collections.abc import Callable, Generator
from typing import Any
from unittest.mock import patch

import pytest

from daq_config_server.converters._converters import (
    beamline_parameters_to_dict,
    display_config_to_dict,
    undulator_energy_gap_lut_to_dict,
    xml_to_dict,
)
from tests.constants import ServerFilePaths, TestDataPaths


@pytest.fixture
def mock_file_converter_map() -> Generator[dict[str, Callable[[str], Any]], None, None]:
    with patch(
        "daq_config_server.converters._file_converter_map.FILE_TO_CONVERTER_MAP",
        {
            str(TestDataPaths.TEST_GOOD_XML_PATH): xml_to_dict,
            str(
                TestDataPaths.TEST_BEAMLINE_PARAMETERS_PATH
            ): beamline_parameters_to_dict,
            str(TestDataPaths.TEST_GOOD_LUT_PATH): undulator_energy_gap_lut_to_dict,
            str(TestDataPaths.TEST_GOOD_DISPLAY_CONFIG_PATH): display_config_to_dict,
            str(ServerFilePaths.GOOD_LUT): undulator_energy_gap_lut_to_dict,
        },
    ) as mock_map:
        yield mock_map
