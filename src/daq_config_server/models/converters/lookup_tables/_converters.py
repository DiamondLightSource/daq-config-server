from typing import Any

from daq_config_server.models.converters import parse_value, remove_comments

from ._models import GenericLookupTable


def parse_lut(contents: str, *params: tuple[str, type | None]) -> GenericLookupTable:
    """Converts a lookup table to a pydantic model, containing the names of each column
    and the rows as a 2D list.

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
    return GenericLookupTable(column_names=column_names, rows=rows)


def detector_xy_lut(contents: str) -> GenericLookupTable:
    return parse_lut(
        contents,
        ("detector_distances_mm", float),
        ("beam_centre_x_mm", float),
        ("beam_centre_y_mm", float),
    )


def beamline_pitch_lut(contents: str) -> GenericLookupTable:
    return parse_lut(contents, ("bragg_angle_deg", float), ("pitch_mrad", float))


def beamline_roll_lut(contents: str) -> GenericLookupTable:
    return parse_lut(contents, ("bragg_angle_deg", float), ("roll_mrad", float))


def undulator_energy_gap_lut(contents: str) -> GenericLookupTable:
    return parse_lut(contents, ("energy_eV", int), ("gap_mm", float))
