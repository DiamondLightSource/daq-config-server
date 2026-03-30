from typing import Generic, TypeVar

from pydantic import model_validator

from daq_config_server.models.base_model import ConfigModel

T = TypeVar("T", bound=ConfigModel)


class PerZoomLevel(ConfigModel, Generic[T]):
    zoom_levels: dict[float, T]
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
