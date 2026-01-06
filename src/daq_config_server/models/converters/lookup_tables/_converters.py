from typing import Any

from daq_config_server.models.converters import parse_value, remove_comments

from ._models import (
    BeamlinePitchLookupTable,
    BeamlineRollLookupTable,
    DetectorXYLookupTable,
    GenericLookupTable,
    UndulatorEnergyGapLookupTable,
)

IGNORE_LINES_STARTING_WITH = ("Units", "ScannableUnits", "ScannableNames")


def parse_lut_rows(
    contents: str, types: list[type | None] | None = None
) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for line in remove_comments(contents.splitlines()):
        if line.startswith(IGNORE_LINES_STARTING_WITH):
            continue
        rows.append(
            [
                parse_value(value, types[i] if types else None)
                for i, value in enumerate(line.split())
            ]
        )
    return rows


def parse_lut(contents: str, *params: tuple[str, type | None]) -> GenericLookupTable:
    """Converts a lookup table to a pydantic model, containing the names of each column
    and the rows as a 2D list.

    Any args after the contents provide the column names and optionally, python types
    for values in a column to be converted to. e.g: ("energy_EV", float),
    ("pixels", int). If a type is provided, the values in that column will be converted
    to that type. Otherwise, the type will be inferred. Units should be included in the
    column name.
    """
    column_names = [param[0] for param in params]
    types = [param[1] for param in params]
    rows = parse_lut_rows(contents, types)
    return GenericLookupTable(column_names=column_names, rows=rows)


def detector_xy_lut(contents: str) -> DetectorXYLookupTable:
    return DetectorXYLookupTable(rows=parse_lut_rows(contents))


def beamline_pitch_lut(contents: str) -> BeamlinePitchLookupTable:
    return BeamlinePitchLookupTable(rows=parse_lut_rows(contents))


def beamline_roll_lut(contents: str) -> BeamlineRollLookupTable:
    return BeamlineRollLookupTable(rows=parse_lut_rows(contents))


def undulator_energy_gap_lut(contents: str) -> UndulatorEnergyGapLookupTable:
    return UndulatorEnergyGapLookupTable(rows=parse_lut_rows(contents))


def i09_hu_undulator_energy_gap_lut(contents: str) -> GenericLookupTable:
    return parse_lut(
        contents,
        ("order", int),
        ("ring_energy_gev", float),
        ("magnetic_field_t", float),
        ("energy_min_ev", float),
        ("energy_max_ev", float),
        ("gap_min_mm", float),
        ("gap_max_mm", float),
        ("gap_offset_mm", float),
    )
