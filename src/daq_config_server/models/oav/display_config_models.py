from typing import Self

from daq_config_server.models.base_model import ConfigModel
from daq_config_server.models.oav.per_zoom_level import PerZoomLevel
from daq_config_server.models.utils import camel_to_snake_case, remove_comments


class DisplayConfigData(ConfigModel):
    crosshair_x: int
    crosshair_y: int
    top_left_x: int
    top_left_y: int
    bottom_right_x: int
    bottom_right_y: int


class DisplayConfig(PerZoomLevel[DisplayConfigData]):
    @classmethod
    def from_contents(cls, contents: str) -> Self:
        lines = contents.splitlines()
        config_dict: dict[float, dict[str, int | float]] = {}
        zoom_level = None

        for line in remove_comments(lines):
            key, value = (item.strip() for item in line.split("=", 1))
            key = camel_to_snake_case(key)
            if key == "zoom_level":
                zoom_level = float(value)
                assert zoom_level not in config_dict.keys(), (
                    f"Multiple instances of zoomLevel {zoom_level}"
                )
                config_dict[zoom_level] = {}
                continue

            assert zoom_level is not None, "File must start with a zoom level"
            assert key not in config_dict[zoom_level].keys(), (
                "File can't have repeated keys for a given zoom level"
            )
            config_dict[zoom_level][key] = float(value)

        zoom_levels = {
            key: DisplayConfigData.model_validate(value)
            for key, value in config_dict.items()
        }
        return cls(zoom_levels=zoom_levels)
