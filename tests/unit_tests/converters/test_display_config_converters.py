import json

import pytest
from tests.constants import TestDataPaths

from daq_config_server.models.converters.display_config import (
    DisplayConfig,
    DisplayConfigData,
    display_config_to_model,
)


def test_display_config_to_model_gives_expected_result_and_can_be_jsonified():
    with open(TestDataPaths.TEST_GOOD_DISPLAY_CONFIG_PATH) as f:
        contents = f.read()
    expected = DisplayConfig(
        zoom_levels={
            1.0: DisplayConfigData(
                bottom_right_x=410,
                bottom_right_y=278,
                crosshair_x=541,
                crosshair_y=409,
                top_left_x=383,
                top_left_y=253,
            ),
            2.5: DisplayConfigData(
                bottom_right_x=388,
                bottom_right_y=322,
                crosshair_x=551,
                crosshair_y=410,
                top_left_x=340,
                top_left_y=283,
            ),
        }
    )
    result = display_config_to_model(contents)
    assert result == expected
    json.dumps(result.model_dump())


def test_display_config_with_wrong_zoom_levels_causes_error():
    zoom_levels = {
        1.0: DisplayConfigData(
            bottom_right_x=410,
            bottom_right_y=278,
            crosshair_x=541,
            crosshair_y=409,
            top_left_x=383,
            top_left_y=253,
        ),
        2.5: DisplayConfigData(
            bottom_right_x=388,
            bottom_right_y=322,
            crosshair_x=551,
            crosshair_y=410,
            top_left_x=340,
            top_left_y=283,
        ),
    }
    with pytest.raises(
        ValueError,
        match="Zoom levels {1.0, 2.5} do not match required zoom levels: {1.0, 3.0}",
    ):
        DisplayConfig(zoom_levels=zoom_levels, required_zoom_levels=({1.0, 3.0}))
