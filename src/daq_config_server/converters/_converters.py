from typing import Any, cast

import xmltodict

from daq_config_server.converters._converter_utils import (
    BEAMLINE_PARAMETER_KEYWORDS,
    parse_lut_to_dict,
    parse_value,
    remove_comments,
)


def beamline_parameters_to_dict(contents: str) -> dict[str, Any]:
    """Extracts the key value pairs from a beamline parameters file. If the value
    is in BEAMLINE_PARAMETER_KEYWORDS, it leaves it as a string. Otherwise, it is
    converted to a number or bool."""
    lines = contents.splitlines()
    config_lines_sep_key_and_value = [
        line.translate(str.maketrans("", "", " \n\t\r")).split("=")
        for line in remove_comments(lines)
    ]
    config_pairs: list[tuple[str, Any]] = [
        cast(tuple[str, Any], param)
        for param in config_lines_sep_key_and_value
        if len(param) == 2
    ]
    for i, (param, value) in enumerate(config_pairs):
        if value not in BEAMLINE_PARAMETER_KEYWORDS:
            config_pairs[i] = (
                param,
                parse_value(value),
            )
    return dict(config_pairs)


def display_config_to_dict(contents: str) -> dict[str, dict[str, int | float]]:
    """Converts a display config file into a dict. Every zoom level entry in the
    configuration file forms a key in the dict, with value being another dict. This
    inner dict contains all the key value pairs of the rows following each zoom level.

    Example input:

    zoomLevel = 1.0
    crosshairX = 500
    crosshairY = 600
    zoomLevel = 2.0
    crosshairX = 700
    crosshairY = 600

    Example output:
    {
        1.0: {"crosshairX": 500, "crosshairY": 600},
        2.0: {"crosshairX": 700, "crosshairY": 800},
    }
    """
    lines = contents.splitlines()
    config_dict: dict[str, dict[str, int | float]] = {}
    zoom_level = None

    for line in remove_comments(lines):
        if line[0] == "#":
            continue

        key, value = (item.strip() for item in line.split("=", 1))
        if key == "zoomLevel":
            zoom_level = value
            assert zoom_level not in config_dict.keys(), (
                f"Multiple instances of zoomLevel {zoom_level}"
            )
            config_dict[zoom_level] = {}
            continue

        assert zoom_level is not None, "File must start with a zoom level"
        assert key not in config_dict[zoom_level].keys(), (
            "File can't have repeated keys for a given zoom level"
        )
        config_dict[zoom_level][key] = parse_value(value)
    return config_dict


def xml_to_dict(contents: str) -> dict[str, Any]:
    return xmltodict.parse(contents)


def detector_xy_lut_to_dict(contents: str):
    return parse_lut_to_dict(
        contents,
        ("detector_distances_mm", float),
        ("beam_centre_x_mm", float),
        ("beam_centre_y_mm", float),
    )


def beamline_pitch_lut_to_dict(contents: str):
    return parse_lut_to_dict(
        contents, ("bragg_angle_deg", float), ("pitch_mrad", float)
    )


def beamline_roll_lut_to_dict(contents: str):
    return parse_lut_to_dict(contents, ("bragg_angle_deg", float), ("roll_mrad", float))


def undulator_energy_gap_lut_to_dict(contents: str):
    return parse_lut_to_dict(contents, ("energy_eV", int), ("gap_mm", float))
