from collections.abc import Callable, Generator, Mapping
from typing import Any
from unittest.mock import patch

import pytest
import xmltodict

from daq_config_server.models import (
    ConfigModel,
    beamline_parameters_to_dict,
)
from daq_config_server.models.lookup_tables.insertion_device import (
    UndulatorEnergyGapLookupTable,
)
from daq_config_server.models.oav import DisplayConfig
from tests.constants import ServerFilePaths, TestDataPaths


@pytest.fixture
def mock_file_converter_map() -> Generator[
    Mapping[str, Callable[[str], ConfigModel | dict[str, Any]]], None, None
]:
    with patch(
        "daq_config_server.app._routes.FILE_TO_CONVERTER_MAP",
        {
            str(TestDataPaths.TEST_GOOD_XML_PATH): xmltodict.parse,
            str(
                TestDataPaths.TEST_BEAMLINE_PARAMETERS_PATH
            ): beamline_parameters_to_dict,
            str(
                TestDataPaths.TEST_GOOD_LUT_PATH
            ): UndulatorEnergyGapLookupTable.from_contents,
            str(
                TestDataPaths.TEST_GOOD_DISPLAY_CONFIG_PATH
            ): DisplayConfig.from_contents,
            str(ServerFilePaths.GOOD_LUT): UndulatorEnergyGapLookupTable.from_contents,
        },
    ) as mock_map:
        yield mock_map
