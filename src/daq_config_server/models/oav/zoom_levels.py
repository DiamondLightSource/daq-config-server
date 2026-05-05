from typing import Self

import xmltodict

from daq_config_server.models.base_model import ConfigModel
from daq_config_server.models.oav.per_zoom_level import PerZoomLevel
from daq_config_server.models.utils import camel_to_snake_case


class ZoomLevelData(ConfigModel):
    position: int
    microns_per_x_pixel: float
    microns_per_y_pixel: float


class ZoomLevels(PerZoomLevel[ZoomLevelData]):
    tolerance: float

    @classmethod
    def from_jcamera_man_zoom_levels(cls, contents: str) -> Self:
        config_dict = xmltodict.parse(contents)
        zoom_levels_list: list[dict[str, str]] = config_dict["JCameraManSettings"][
            "levels"
        ]["zoomLevel"]
        zoom_levels: dict[float, ZoomLevelData] = {}
        for zoom_level in zoom_levels_list:
            level = float(zoom_level["level"])
            new_zoom_level = {
                camel_to_snake_case(key): value
                for key, value in zoom_level.items()
                if key != "level"
            }
            zoom_levels[level] = ZoomLevelData.model_validate(new_zoom_level)
        return cls(
            zoom_levels=zoom_levels,
            tolerance=config_dict["JCameraManSettings"]["tolerance"],
        )
