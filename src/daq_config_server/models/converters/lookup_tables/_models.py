from abc import abstractmethod
from typing import Generic, Literal, TypeVar, get_args

from pydantic import model_validator

from daq_config_server.models.converters import ConfigModel

ColumnNameT = TypeVar("ColumnNameT", bound=str)


class LookupTableBase(ConfigModel, Generic[ColumnNameT]):
    rows: list[list[int | float]]

    @model_validator(mode="after")
    def check_row_length_matches_n_columns(self):
        column_names = self.get_column_names()
        n_columns = len(column_names)
        for row in self.rows:
            if len(row) != n_columns:
                raise ValueError(
                    f"Length of row {row} does not match number "
                    f"of columns: {column_names}"
                )
        return self

    def columns(self) -> list[list[int | float]]:
        return [[row[i] for row in self.rows] for i in range(len(self.rows[0]))]

    def get_value(
        self,
        search_column_name: ColumnNameT,
        value: int | float,
        target_column_name: ColumnNameT,
        value_must_exist: bool = True,
    ) -> int | float:
        """Look up a value in one column and return the corresponding entry from another
        column.

        Args:
            column_name (ColumnNameT): The name of the column to search in.
            value (int | float): The numeric value to look for within `column_name`.
            target_column_name (ColumnNameT): The name of the column from which to
            return the corresponding entry (same row as the matched value).
            value_must_exist (bool, optional): If true, value must exist in the LUT or
            an error will be thrown. Otherwise, the closest value will be used.
            Defaults to True.

        Returns:
            int | float: The entry from `target_column_name` in the row where the
        matching (or closest) value was found in `column_name`.
        """
        column_names = self.get_column_names()
        search_column_index = column_names.index(search_column_name)
        target_column_index = column_names.index(target_column_name)
        column = [row[search_column_index] for row in self.rows]

        closest_value = (
            min(column, key=lambda x: abs(x - value)) if not value_must_exist else value
        )
        try:
            target_row = self.rows[column.index(closest_value)]
        except ValueError as e:
            raise ValueError(
                f"'{closest_value}' doesn't exist in column '"
                f"{search_column_name}': {column}"
            ) from e

        return target_row[target_column_index]

    @abstractmethod
    def get_column_names(
        self,
    ) -> list[ColumnNameT]: ...


class GenericLookupTable(LookupTableBase[str]):
    column_names: list[str]

    def get_column_names(self) -> list[str]:
        return self.column_names


DETECTOR_XY_COLUMN_NAMES = Literal[
    "detector_distances_mm", "beam_centre_x_mm", "beam_centre_y_mm"
]


class DetectorXYLookupTable(LookupTableBase[DETECTOR_XY_COLUMN_NAMES]):
    def get_column_names(self) -> list[DETECTOR_XY_COLUMN_NAMES]:
        return list(get_args(DETECTOR_XY_COLUMN_NAMES))
