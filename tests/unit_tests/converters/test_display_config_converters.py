import json

import pytest
from tests.constants import TestDataPaths

from daq_config_server.converters.display_config._converters import (
    display_config_to_model,
)
from daq_config_server.models import (
    DisplayConfig,
    DisplayConfigData,
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
    with pytest.raises(
        ValueError,
        match="Zoom levels {1.0, 2.5} do not match required zoom levels: {1.0, 3.0}",
    ):
        DisplayConfig(zoom_levels=zoom_levels, required_zoom_levels=({1.0, 3.0}))
