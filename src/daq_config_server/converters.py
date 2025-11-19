import ast
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

import xmltodict

BEAMLINE_PARAMETER_KEYWORDS = ["FB", "FULL", "deadtime"]


def _remove_comments(lines: list[str]) -> list[str]:
    return [
        line.strip().split("#", 1)[0].strip()
        for line in lines
        if line.strip().split("#", 1)[0]
    ]


def _parse_value(value: str):
    return ast.literal_eval(value.replace("Yes", "True").replace("No", "False"))


def _parse_lut_to_dict(
    contents: str, *params: tuple[str, str, type]
) -> dict[str, dict[str, str] | list[dict[str, Any]]]:
    return {
        "units": {key: unit for param in params for key, unit in [param[:2]]},
        "data": [
            {params[i][0]: params[i][2](value) for i, value in enumerate(line.split())}
            for line in _remove_comments(contents.splitlines())
            if not line.startswith("Units")
        ],
    }


def beamline_parameters_to_dict(contents: str) -> dict[str, Any]:
    lines = contents.splitlines()
    config_lines_sep_key_and_value = [
        line.translate(str.maketrans("", "", " \n\t\r")).split("=")
        for line in _remove_comments(lines)
    ]
    config_pairs: list[tuple[str, Any]] = [
        cast(tuple[str, Any], param)
        for param in config_lines_sep_key_and_value
        if len(param) == 2
    ]
    for i, (param, value) in enumerate(config_pairs):
        # BEAMLINE_PARAMETER_KEYWORDS effectively raw string but whitespace removed
        if value not in BEAMLINE_PARAMETER_KEYWORDS:
            config_pairs[i] = (
                param,
                _parse_value(value),
            )
    return dict(config_pairs)


def display_config_to_dict(contents: str) -> dict[str, dict[str, int | float | str]]:
    lines = contents.splitlines()

    config_dict: dict[str, dict[str, int | float | str]] = {}
    zoom_level = None

    for line in _remove_comments(lines):
        if line[0] == "#":
            continue

        key, value = (item.strip() for item in line.split("=", 1))
        if key == "zoomLevel":
            zoom_level = value
            config_dict[zoom_level] = {}
            continue

        assert zoom_level is not None, (
            "Display configuration file in wrong format, unable to parse"
        )

        try:
            config_dict[zoom_level][key] = float(value) if "." in value else int(value)
        except ValueError:
            config_dict[zoom_level][key] = value
    return config_dict


def xml_to_dict(contents: str) -> dict[str, Any]:
    return xmltodict.parse(contents)


def detector_xy_lut_to_dict(contents: str):
    return _parse_lut_to_dict(
        contents,
        ("detector_distances", "mm", float),
        ("beam_centre_x", "mm", float),
        ("beam_centre_y", "mm", float),
    )


def beamline_pitch_lut_to_dict(contents: str):
    return _parse_lut_to_dict(
        contents, ("bragg_angle", "degrees", float), ("pitch", "mrad", float)
    )


def beamline_roll_lut_to_dict(contents: str):
    return _parse_lut_to_dict(
        contents, ("bragg_angle", "degrees", float), ("roll", "mrad", float)
    )


def undulator_energy_gap_lut_to_dict(contents: str):
    return _parse_lut_to_dict(contents, ("energy", "eV", int), ("gap", "mm", float))


FILE_TO_CONVERTER_MAP: dict[str, Callable[[str], Any]] = {
    "/dls_sw/i23/software/aithre/aithre_display.configuration": display_config_to_dict,
    "/dls_sw/i03/software/gda_versions/var/display.configuration": display_config_to_dict,
    "/dls_sw/i04/software/bluesky/scratch/display.configuration": display_config_to_dict,
    "/dls_sw/i19-1/software/daq_configuration/domain/display.configuration": display_config_to_dict,
    "/dls_sw/i24/software/gda_versions/var/display.configuration": display_config_to_dict,
    "/dls_sw/i03/software/gda/configurations/i03-config/xml/jCameraManZoomLevels.xml": xml_to_dict,
    "/dls_sw/i04/software/bluesky/scratch/jCameraManZoomLevels.xml": xml_to_dict,
    "/dls_sw/i19-1/software/gda_versions/gda/config/xml/jCameraManZoomLevels.xml": xml_to_dict,
    "/dls_sw/i24/software/gda_versions/gda/config/xml/jCameraManZoomLevels.xml": xml_to_dict,
    "/dls_sw/i03/software/daq_configuration/domain/beamlineParameters": beamline_parameters_to_dict,
    "/dls_sw/i04/software/daq_configuration/domain/beamlineParameters": beamline_parameters_to_dict,
    "/dls_sw/i03/software/daq_configuration/lookup/DetDistToBeamXYConverter.txt": detector_xy_lut_to_dict,
    "/dls_sw/i04/software/daq_configuration/lookup/DetDistToBeamXYConverter.txt": detector_xy_lut_to_dict,
    "/dls_sw/i04-1/software/daq_configuration/lookup/DetDistToBeamXYConverter.txt": detector_xy_lut_to_dict,
    "/dls_sw/i19-1/software/daq_configuration/lookup/DetDistToBeamXYConverter.txt": detector_xy_lut_to_dict,
    "/dls_sw/i23/software/daq_configuration/lookup/DetDistToBeamXYConverter.txt": detector_xy_lut_to_dict,
    "/dls_sw/i24/software/daq_configuration/lookup/DetDistToBeamXYConverter.txt": detector_xy_lut_to_dict,
    "/dls_sw/i03/software/daq_configuration/lookup/BeamLineEnergy_DCM_Pitch_converter.txt": beamline_pitch_lut_to_dict,
    "/dls_sw/i03/software/daq_configuration/lookup/BeamLineEnergy_DCM_Roll_converter.txt": beamline_roll_lut_to_dict,
    "/dls_sw/i03/software/daq_configuration/lookup/BeamLine_Undulator_toGap.txt": undulator_energy_gap_lut_to_dict,
}


def get_converted_file_contents(file_path: Path) -> Any:
    with file_path.open("r", encoding="utf-8") as f:
        raw_contents = f.read()
    print(str(file_path))
    if (converter := FILE_TO_CONVERTER_MAP.get(str(file_path))) is not None:
        return converter(raw_contents)
    return json.loads(raw_contents)
