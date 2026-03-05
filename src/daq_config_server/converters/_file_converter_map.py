from collections.abc import Callable
from typing import Any

import xmltodict

from daq_config_server.models._base_model import ConfigModel
from daq_config_server.models.beamline_parameters._converters import (
    beamline_parameters_to_dict,
)
from daq_config_server.models.display_config._converters import (
    display_config_to_model,
)
from daq_config_server.models.lookup_tables.insertion_device._converters import (
    parse_i09_hu_undulator_energy_gap_lut,
)
from daq_config_server.models.lookup_tables.insertion_device._models import (
    UndulatorEnergyGapLookupTable,
)
from daq_config_server.models.lookup_tables.mx._models import (
    BeamlinePitchLookupTable,
    BeamlineRollLookupTable,
    DetectorXYLookupTable,
)

FILE_TO_CONVERTER_MAP: dict[str, Callable[[str], ConfigModel | dict[str, Any]]] = {  # type: ignore
    "/tests/test_data/test_good_lut.txt": UndulatorEnergyGapLookupTable.from_contents,  # For system tests # noqa: E501
    "/dls_sw/i23/software/aithre/aithre_display.configuration": display_config_to_model,
    "/dls_sw/i03/software/gda_versions/var/display.configuration": display_config_to_model,  # noqa: E501
    "/dls_sw/i04/software/bluesky/scratch/display.configuration": display_config_to_model,  # noqa: E501
    "/dls_sw/i19-1/software/daq_configuration/domain/display.configuration": display_config_to_model,  # noqa: E501
    "/dls_sw/i24/software/gda_versions/var/display.configuration": display_config_to_model,  # noqa: E501
    "/dls_sw/i03/software/gda/configurations/i03-config/xml/jCameraManZoomLevels.xml": xmltodict.parse,  # noqa: E501
    "/dls_sw/i04/software/bluesky/scratch/jCameraManZoomLevels.xml": xmltodict.parse,
    "/dls_sw/i19-1/software/gda_versions/gda/config/xml/jCameraManZoomLevels.xml": xmltodict.parse,  # noqa: E501
    "/dls_sw/i24/software/gda_versions/gda/config/xml/jCameraManZoomLevels.xml": xmltodict.parse,  # noqa: E501
    "/dls_sw/i03/software/daq_configuration/domain/beamlineParameters": beamline_parameters_to_dict,  # noqa: E501
    "/dls_sw/i04/software/daq_configuration/domain/beamlineParameters": beamline_parameters_to_dict,  # noqa: E501
    "/dls_sw/i03/software/daq_configuration/lookup/DetDistToBeamXYConverter.txt": DetectorXYLookupTable.from_contents,  # noqa: E501
    "/dls_sw/i04/software/daq_configuration/lookup/DetDistToBeamXYConverter.txt": DetectorXYLookupTable.from_contents,  # noqa: E501
    "/dls_sw/i04-1/software/daq_configuration/lookup/DetDistToBeamXYConverter.txt": DetectorXYLookupTable.from_contents,  # noqa: E501
    "/dls_sw/i19-1/software/daq_configuration/lookup/DetDistToBeamXYConverter.txt": DetectorXYLookupTable.from_contents,  # noqa: E501
    "/dls_sw/i23/software/daq_configuration/lookup/DetDistToBeamXYConverter.txt": DetectorXYLookupTable.from_contents,  # noqa: E501
    "/dls_sw/i24/software/daq_configuration/lookup/DetDistToBeamXYConverter.txt": DetectorXYLookupTable.from_contents,  # noqa: E501
    "/dls_sw/i03/software/daq_configuration/lookup/BeamLineEnergy_DCM_Pitch_converter.txt": BeamlinePitchLookupTable.from_contents,  # noqa: E501
    "/dls_sw/i03/software/daq_configuration/lookup/BeamLineEnergy_DCM_Roll_converter.txt": BeamlineRollLookupTable.from_contents,  # noqa: E501
    "/dls_sw/i03/software/daq_configuration/lookup/BeamLine_Undulator_toGap.txt": UndulatorEnergyGapLookupTable.from_contents,  # noqa: E501
    "/dls_sw/i09-1/software/gda/workspace_git/gda-diamond.git/configurations/i09-1-shared/lookupTables/IIDCalibrationTable.txt": parse_i09_hu_undulator_energy_gap_lut,  # noqa: E501
}
