from pydantic import model_validator

from daq_config_server.models.converters import ConfigModel


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

    def get_value(
        self,
        column_name: str,
        value: int | float,
        target_column_name: str,
        value_must_exist: bool = True,
    ) -> int | float:
        column_index = self.column_names.index(column_name)
        column = [row[column_index] for row in self.rows]
        target_column_index = self.column_names.index(target_column_name)

        closest_value = (
            min(column, key=lambda x: abs(x - value)) if not value_must_exist else value
        )
        target_row = self.rows[column.index(closest_value)]

        return target_row[target_column_index]

    def columns(self) -> list[list[int | float]]:
        return [[row[i] for row in self.rows] for i in range(len(self.column_names))]
