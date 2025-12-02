from typing import Any

import xmltodict

from daq_config_server.converters._converter_utils import (
    BEAMLINE_PARAMETER_KEYWORDS,
    GenericLut,
    parse_lut,
    parse_value,
    remove_comments,
)
from daq_config_server.converters.models import DisplayConfig, DisplayConfigData


def beamline_parameters_to_dict(contents: str) -> dict[str, Any]:
    """Extracts the key value pairs from a beamline parameters file. If the value
    is in BEAMLINE_PARAMETER_KEYWORDS, it leaves it as a string. Otherwise, it is
    converted to a number or bool."""
    lines = contents.splitlines()
    config_pairs: dict[str, Any] = {}

    # Get dict of parameter keys and values
    for line in remove_comments(lines):
        splitline = line.split("=")
        if len(splitline) >= 2:
            param, value = line.split("=")
            if param.strip() in config_pairs:
                raise ValueError(f"Repeated key in parameters: {param}")
            config_pairs[param.strip()] = value.strip()

    # Parse each value
    for param, value in config_pairs.items():
        if value not in BEAMLINE_PARAMETER_KEYWORDS:
            config_pairs[param] = parse_value(value)
    return dict(config_pairs)


def display_config_to_model(contents: str) -> DisplayConfig:
    lines = contents.splitlines()
    config_dict: dict[float, dict[str, int | float]] = {}
    zoom_level = None

    for line in remove_comments(lines):
        key, value = (item.strip() for item in line.split("=", 1))
        if key == "zoomLevel":
            zoom_level = float(value)
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
    zoom_levels = {
        key: DisplayConfigData.model_validate(value)
        for key, value in config_dict.items()
    }

    return DisplayConfig(zoom_levels=zoom_levels)


def xml_to_dict(contents: str) -> dict[str, Any]:
    return xmltodict.parse(contents)


def detector_xy_lut(contents: str) -> GenericLut:
    return parse_lut(
        contents,
        ("detector_distances_mm", float),
        ("beam_centre_x_mm", float),
        ("beam_centre_y_mm", float),
    )


def beamline_pitch_lut(contents: str) -> GenericLut:
    return parse_lut(contents, ("bragg_angle_deg", float), ("pitch_mrad", float))


def beamline_roll_lut(contents: str) -> GenericLut:
    return parse_lut(contents, ("bragg_angle_deg", float), ("roll_mrad", float))


def undulator_energy_gap_lut(contents: str) -> GenericLut:
    return parse_lut(contents, ("energy_eV", int), ("gap_mm", float))
