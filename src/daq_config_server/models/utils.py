import ast
import re
from collections.abc import Iterable
from typing import Any


def remove_comments(lines: Iterable[str]) -> list[str]:
    return [
        line.strip().split("#", 1)[0].strip()
        for line in lines
        if line.strip().split("#", 1)[0]
    ]


DEFAULT_REPLACEMENTS = {"Yes": "True", "No": "False", "true": "True", "false": "False"}


def parse_value(
    value: str,
    convert_to: type | None = None,
    replacements: dict[str, str] = DEFAULT_REPLACEMENTS,
) -> Any:
    """Convert a string value into an appropriate Python type. Optionally provide a type
    to convert to. If not given, the type will be inferred.
    """
    value = ast.literal_eval(replacements.get(value, value))
    if convert_to:
        value = convert_to(value)
    return value


def camel_to_snake_case(value: str) -> str:
    return re.sub(r"([a-z])([A-Z])", r"\1_\2", value).lower()


DEFAULT_IGNORE_LINES_STARTING_WITH = ("Units", "ScannableUnits", "ScannableNames")


def parse_lut_rows(
    contents: str,
    types: list[type | None] | None = None,
    ignore_lines_starting_with: tuple[str, ...] = DEFAULT_IGNORE_LINES_STARTING_WITH,
) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for line in remove_comments(contents.splitlines()):
        if line.startswith(ignore_lines_starting_with):
            continue
        rows.append(
            [
                parse_value(value, types[i] if types else None)
                for i, value in enumerate(line.split())
            ]
        )
    return rows
