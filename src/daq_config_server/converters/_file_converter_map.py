from collections.abc import Callable
from typing import Any

import xmltodict
from pydantic import BaseModel

from daq_config_server.converters._converters import (
    beamline_parameters_to_dict,
    beamline_pitch_lut,
    beamline_roll_lut,
    detector_xy_lut,
    display_config_to_model,
    undulator_energy_gap_lut,
)

FILE_TO_CONVERTER_MAP: dict[str, Callable[[str], BaseModel | dict[str, Any]]] = {  # type: ignore
    "/tests/test_data/test_good_lut.txt": undulator_energy_gap_lut,  # For system tests # noqa
    "/dls_sw/i23/software/aithre/aithre_display.configuration": display_config_to_model,
    "/dls_sw/i03/software/gda_versions/var/display.configuration": display_config_to_model,  # noqa
    "/dls_sw/i04/software/bluesky/scratch/display.configuration": display_config_to_model,  # noqa
    "/dls_sw/i19-1/software/daq_configuration/domain/display.configuration": display_config_to_model,  # noqa
    "/dls_sw/i24/software/gda_versions/var/display.configuration": display_config_to_model,  # noqa
    "/dls_sw/i03/software/gda/configurations/i03-config/xml/jCameraManZoomLevels.xml": xmltodict.parse,  # noqa
    "/dls_sw/i04/software/bluesky/scratch/jCameraManZoomLevels.xml": xmltodict.parse,
    "/dls_sw/i19-1/software/gda_versions/gda/config/xml/jCameraManZoomLevels.xml": xmltodict.parse,  # noqa
    "/dls_sw/i24/software/gda_versions/gda/config/xml/jCameraManZoomLevels.xml": xmltodict.parse,  # noqa
    "/dls_sw/i03/software/daq_configuration/domain/beamlineParameters": beamline_parameters_to_dict,  # noqa
    "/dls_sw/i04/software/daq_configuration/domain/beamlineParameters": beamline_parameters_to_dict,  # noqa
    "/dls_sw/i03/software/daq_configuration/lookup/DetDistToBeamXYConverter.txt": detector_xy_lut,  # noqa
    "/dls_sw/i04/software/daq_configuration/lookup/DetDistToBeamXYConverter.txt": detector_xy_lut,  # noqa
    "/dls_sw/i04-1/software/daq_configuration/lookup/DetDistToBeamXYConverter.txt": detector_xy_lut,  # noqa
    "/dls_sw/i19-1/software/daq_configuration/lookup/DetDistToBeamXYConverter.txt": detector_xy_lut,  # noqa
    "/dls_sw/i23/software/daq_configuration/lookup/DetDistToBeamXYConverter.txt": detector_xy_lut,  # noqa
    "/dls_sw/i24/software/daq_configuration/lookup/DetDistToBeamXYConverter.txt": detector_xy_lut,  # noqa
    "/dls_sw/i03/software/daq_configuration/lookup/BeamLineEnergy_DCM_Pitch_converter.txt": beamline_pitch_lut,  # noqa
    "/dls_sw/i03/software/daq_configuration/lookup/BeamLineEnergy_DCM_Roll_converter.txt": beamline_roll_lut,  # noqa
    "/dls_sw/i03/software/daq_configuration/lookup/BeamLine_Undulator_toGap.txt": undulator_energy_gap_lut,  # noqa
}
