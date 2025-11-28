import ast
from typing import Any

from pydantic import BaseModel, model_validator

BEAMLINE_PARAMETER_KEYWORDS = ["FB", "FULL", "deadtime"]


class ConverterParseError(Exception): ...


def remove_comments(lines: list[str]) -> list[str]:
    return [
        line.strip().split("#", 1)[0].strip()
        for line in lines
        if line.strip().split("#", 1)[0]
    ]


def parse_value(value: str, convert_to: type | None = None) -> Any:
    """Convert a string value into an appropriate Python type. Optionally provide a type
    to convert to. If not given, the type will be inferred.
    """
    value = ast.literal_eval(value.replace("Yes", "True").replace("No", "False"))
    if convert_to:
        value = convert_to(value)
    return value


class GenericLut(BaseModel):
    column_names: list[str]
    rows: list[list[int | float]]

    @model_validator(mode="after")
    def check_row_length_matches_n_columns(self):
        n_columns = len(self.column_names)
        for row in self.rows:
            if len(row) != n_columns:
                raise ValueError(
                    f"Length of row {row} does not match number \
                    of columns: {self.column_names}"
                )
        return self


def parse_lut(contents: str, *params: tuple[str, type | None]) -> GenericLut:
    """Converts a lookup table to a dict, containing the names of each column and
    the rows as a 2D list.

    Any args after the contents provide the column names and optionally, python types
    for values in a column to be converted to. e.g: (energy_EV, float), (pixels, int).
    If a type is provided, the values in that column will be converted to that type.
    Otherwise, the type will be inferred. Units should be included in the column name.
    """
    rows: list[list[Any]] = []
    column_names = [param[0] for param in params]
    types = [param[1] for param in params]
    for line in remove_comments(contents.splitlines()):
        if line.startswith("Units"):
            continue
        rows.append(
            [parse_value(value, types[i]) for i, value in enumerate(line.split())]
        )
    return GenericLut(column_names=column_names, rows=rows)
