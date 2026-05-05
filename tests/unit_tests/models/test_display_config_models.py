import json

import pytest

from daq_config_server.models.oav import DisplayConfig, DisplayConfigData
from daq_config_server.models.oav.zoom_levels import ZoomLevelData, ZoomLevels
from tests.constants import TestDataPaths


def test_display_config_from_contents_gives_expected_result_and_can_be_jsonified():
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
    result = DisplayConfig.from_contents(contents)
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


def test_zoom_levels_config_model_can_parse_j_camera_man_file():
    with open(TestDataPaths.TEST_JCAMERA_MAN_ZOOM_LEVELS) as f:
        contents = f.read()
    expected = ZoomLevels(
        zoom_levels={
            1.0: ZoomLevelData(
                position=0, microns_per_x_pixel=2.87, microns_per_y_pixel=2.87
            ),
            2.5: ZoomLevelData(
                position=10, microns_per_x_pixel=2.31, microns_per_y_pixel=2.31
            ),
            5.0: ZoomLevelData(
                position=25, microns_per_x_pixel=1.58, microns_per_y_pixel=1.58
            ),
            7.5: ZoomLevelData(
                position=50, microns_per_x_pixel=0.806, microns_per_y_pixel=0.806
            ),
            10.0: ZoomLevelData(
                position=75, microns_per_x_pixel=0.438, microns_per_y_pixel=0.438
            ),
            15.0: ZoomLevelData(
                position=90, microns_per_x_pixel=0.302, microns_per_y_pixel=0.302
            ),
        },
        tolerance=1.0,
    )
    result = ZoomLevels.from_jcamera_man_zoom_levels(contents)
    assert result == expected
