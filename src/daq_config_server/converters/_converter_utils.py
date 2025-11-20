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
    *params: tuple[str, str, type | None],
) -> dict[str, dict[str, str] | list[dict[str, Any]]]:
    data: list[dict[str, Any]] = []
    data_dict = {
        "units": {key: unit for param in params for key, unit in [param[:2]]},
        "data": data,
    }
    for line in remove_comments(contents.splitlines()):
        if line.startswith("Units"):
            continue
        data.append(
            {
                params[i][0]: parse_value(value, params[i][2])
                for i, value in enumerate(line.split())
            }
        )
    data_dict["data"] = data
    return data_dict
