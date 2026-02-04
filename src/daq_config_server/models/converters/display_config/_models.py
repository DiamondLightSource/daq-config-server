from pydantic import model_validator

from daq_config_server.models.converters import ConfigModel


class DisplayConfigData(ConfigModel):
    crosshair_x: int
    crosshair_y: int
    top_left_x: int
    top_left_y: int
    bottom_right_x: int
    bottom_right_y: int


class DisplayConfig(ConfigModel):
    zoom_levels: dict[float, DisplayConfigData]
    required_zoom_levels: set[float] | None = None

    @model_validator(mode="after")
    def check_zoom_levels_match_required(self):
        existing_keys = set(self.zoom_levels.keys())
        if (
            self.required_zoom_levels is not None
            and self.required_zoom_levels != existing_keys
        ):
            raise ValueError(
                f"Zoom levels {existing_keys} "
                f"do not match required zoom levels: {self.required_zoom_levels}"
            )
        return self
