import ast
from typing import Any

BEAMLINE_PARAMETER_KEYWORDS = ["FB", "FULL", "deadtime"]


class ConverterParseError(Exception): ...


def remove_comments(lines: list[str]) -> list[str]:
    return [
        line.strip().split("#", 1)[0].strip()
        for line in lines
        if line.strip().split("#", 1)[0]
    ]


def parse_value(value: str, convert_to: type | None = None) -> Any:
    """Convert a string value into an appropriate Python type.
    Optionally provide a type to convert to.

    """
    value = value.replace("Yes", "True").replace("No", "False")
    return convert_to(value) if convert_to else ast.literal_eval(value)


def parse_lut_to_dict(
    contents: str,
    *params: tuple[str, type | None],
) -> dict[str, list[str] | list[list[Any]]]:
    """Converts a lookup table to a dict, containing the names of each column and
    the rows as a 2D list.

    Any args after the contents provide the column names and optionally, python types
    for values in a column to be converted to. e.g: (energy_EV, float), (pixels, int).
    If a type is provided, the values in that column will be converted to that type.
    Otherwise, the type will be inferred. Units should be included in the column name.
    """
    data: list[list[Any]] = []
    column_names = [param[0] for param in params]
    types = [param[1] for param in params]
    data_dict = {
        "column_names": column_names,
        "data": data,
    }
    for line in remove_comments(contents.splitlines()):
        if line.startswith("Units"):
            continue
        data.append(
            [parse_value(value, types[i]) for i, value in enumerate(line.split())]
        )
    data_dict["data"] = data
    return data_dict
