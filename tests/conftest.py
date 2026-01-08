from collections.abc import Callable, Generator, Mapping
from typing import Any
from unittest.mock import patch

import pytest
import xmltodict

from daq_config_server.models.converters import ConfigModel
from daq_config_server.models.converters.beamline_parameters import (
    beamline_parameters_to_dict,
)
from daq_config_server.models.converters.display_config import (
    display_config_to_model,
)
from daq_config_server.models.converters.lookup_tables import (
    parse_undulator_energy_gap_lut,
)
from tests.constants import ServerFilePaths, TestDataPaths


@pytest.fixture
def mock_file_converter_map() -> Generator[
    Mapping[str, Callable[[str], ConfigModel | dict[str, Any]]], None, None
]:
    with patch(
        "daq_config_server.models.converters._file_converter_map.FILE_TO_CONVERTER_MAP",
        {
            str(TestDataPaths.TEST_GOOD_XML_PATH): xmltodict.parse,
            str(
                TestDataPaths.TEST_BEAMLINE_PARAMETERS_PATH
            ): beamline_parameters_to_dict,
            str(TestDataPaths.TEST_GOOD_LUT_PATH): parse_undulator_energy_gap_lut,
            str(TestDataPaths.TEST_GOOD_DISPLAY_CONFIG_PATH): display_config_to_model,
            str(ServerFilePaths.GOOD_LUT): parse_undulator_energy_gap_lut,
        },
    ) as mock_map:
        yield mock_map
