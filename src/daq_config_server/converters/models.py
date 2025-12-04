from pydantic import BaseModel, model_validator


class DisplayConfigData(BaseModel):
    crosshairX: int
    crosshairY: int
    topLeftX: int
    topLeftY: int
    bottomRightX: int
    bottomRightY: int


class DisplayConfig(BaseModel):
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


class GenericLookupTable(BaseModel):
    column_names: list[str]
    rows: list[list[int | float]]

    @model_validator(mode="after")
    def check_row_length_matches_n_columns(self):
        n_columns = len(self.column_names)
        for row in self.rows:
            if len(row) != n_columns:
                raise ValueError(
                    f"Length of row {row} does not match number "
                    f"of columns: {self.column_names}"
                )
        return self
