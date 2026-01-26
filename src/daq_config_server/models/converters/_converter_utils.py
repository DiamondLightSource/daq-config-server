import ast
import re
from typing import Any

ALLOWED_BEAMLINE_PARAMETER_STRINGS = ["FB", "FULL", "deadtime"]


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


def camel_to_snake_case(value: str) -> str:
    return re.sub(r"([a-z])([A-Z])", r"\1_\2", value).lower()
