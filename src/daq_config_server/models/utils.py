import re
from collections.abc import Iterable
from typing import Any


def remove_comments(lines: Iterable[str]) -> list[str]:
    return [
        line.strip().split("#", 1)[0].strip()
        for line in lines
        if line.strip().split("#", 1)[0]
    ]


def camel_to_snake_case(value: str) -> str:
    return re.sub(r"([a-z])([A-Z])", r"\1_\2", value).lower()


DEFAULT_IGNORE_LINES_STARTING_WITH = ("Units", "ScannableUnits", "ScannableNames")


def parse_lut_rows(
    contents: str,
    types: list[type[int] | type[float]],
    ignore_lines_starting_with: tuple[str, ...] = DEFAULT_IGNORE_LINES_STARTING_WITH,
) -> list[list[int | float]]:
    rows: list[list[Any]] = []
    for line in remove_comments(contents.splitlines()):
        if line.startswith(ignore_lines_starting_with):
            continue
        rows.append([types[i](value) for i, value in enumerate(line.split())])
    return rows
