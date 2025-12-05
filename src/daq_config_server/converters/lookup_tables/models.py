from pydantic import model_validator

from daq_config_server.converters.models import ConfigModel


class GenericLookupTable(ConfigModel):
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
