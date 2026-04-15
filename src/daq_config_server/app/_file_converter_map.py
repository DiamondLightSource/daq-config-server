from collections.abc import Callable
from pathlib import Path
from typing import Any

import xmltodict
import yaml

from daq_config_server.app._config import ConverterConfig
from daq_config_server.models import DisplayConfig, beamline_parameters_to_dict
from daq_config_server.models.base_model import ConfigModel
from daq_config_server.models.feature_settings.hyperion_feature_settings import (
    HyperionFeatureSettings,
)
from daq_config_server.models.feature_settings.i04_feature_settings import (
    I04FeatureSettings,
)
from daq_config_server.models.i15_1.xpdf_parameters import TemperatureControllersConfig
from daq_config_server.models.lookup_tables import (
    BeamlinePitchLookupTable,
    BeamlineRollLookupTable,
    DetectorXYLookupTable,
)
from daq_config_server.models.lookup_tables.insertion_device import (
    UndulatorEnergyGapLookupTable,
    parse_i09_hu_undulator_energy_gap_lut,
)

DEFAULT_CONVERTER_MAP: dict[str, Callable[[str], ConfigModel | dict[str, Any]]] = {  # type: ignore
    "/tests/test_data/test_good_lut.txt": UndulatorEnergyGapLookupTable.from_contents,  # For system tests # noqa: E501
    "/dls_sw/i23/software/aithre/aithre_display.configuration": DisplayConfig.from_contents,  # noqa: E501
    "/dls_sw/i03/software/gda_versions/var/display.configuration": DisplayConfig.from_contents,  # noqa: E501
    "/dls_sw/i04/software/bluesky/scratch/display.configuration": DisplayConfig.from_contents,  # noqa: E501
    "/dls_sw/i19-1/software/daq_configuration/domain/display.configuration": DisplayConfig.from_contents,  # noqa: E501
    "/dls_sw/i24/software/gda_versions/var/display.configuration": DisplayConfig.from_contents,  # noqa: E501
    "/dls_sw/i03/software/gda/configurations/i03-config/xml/jCameraManZoomLevels.xml": xmltodict.parse,  # noqa: E501
    "/dls_sw/i04/software/bluesky/scratch/jCameraManZoomLevels.xml": xmltodict.parse,  # noqa: E501
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
    "/dls_sw/i04/software/daq_configuration/lookup/BeamLine_Undulator_toGap.txt": UndulatorEnergyGapLookupTable.from_contents,  # noqa: E501
    "/dls_sw/i09-1/software/gda/workspace_git/gda-diamond.git/configurations/i09-1-shared/lookupTables/IIDCalibrationTable.txt": parse_i09_hu_undulator_energy_gap_lut,  # noqa: E501
    "/dls_sw/i04/software/daq_configuration/domain/domain.properties": I04FeatureSettings.from_domain_properties,  # noqa: E501
    "/dls_sw/i03/software/daq_configuration/domain/domain.properties": HyperionFeatureSettings.from_domain_properties,  # noqa: E501
    "/dls_sw/i15-1/software/gda_var/xpdfLocalParameters.xml": TemperatureControllersConfig.from_xpdf_parameters,  # noqa: E501
    "/dls_sw/i23/software/aithre/aithre_oav.xml": xmltodict.parse,  # noqa: E501
}

Converter = Callable[[str], Any]
ConverterMap = Callable[[Path], Converter | None]


def get_converter(path: Path) -> Converter | None:
    """Obtain a converter for converting the specified file to a format for return by
    the config server.
    Args:
        path (Path): path to the file to be converted
    Returns:
        Callable[[str], Any]: the converter which converts a text file to either an
        instance of ConfigModel or something that can be accepted by json.dumps().
        If the converter cannot be resolved then None is returned.
    """
    return _converter_map(path)


def default_converter_map(path: Path) -> Converter | None:
    return DEFAULT_CONVERTER_MAP.get(str(path))


def init_converter_map(config: ConverterConfig):
    global _converter_map
    if config.config_file:
        _converter_map = load_converter_map_from_config_file(Path(config.config_file))
    else:
        _converter_map = default_converter_map


CONVERTER_FUNCS: dict[str, Converter] = {
    "UndulatorEnergyGapLookupTable": UndulatorEnergyGapLookupTable.from_contents,
    "DisplayConfig": DisplayConfig.from_contents,
    "Xml": xmltodict.parse,
    "BeamlineParameters": beamline_parameters_to_dict,
    "DetectorXYLookupTable": DetectorXYLookupTable.from_contents,
    "BeamlinePitchLookupTable": BeamlinePitchLookupTable.from_contents,
    "BeamlineRollLookupTable": BeamlineRollLookupTable.from_contents,
    "I09UndulatorHuEnergyGapLut": parse_i09_hu_undulator_energy_gap_lut,
    "I04FeatureSettings": I04FeatureSettings.from_domain_properties,
    "HyperionFeatureSettings": HyperionFeatureSettings.from_domain_properties,
    "TemperatureControllersConfig": TemperatureControllersConfig.from_xpdf_parameters,
}


def load_converter_map_from_config_file(config_path: Path) -> ConverterMap:
    with config_path.open() as stream:
        path_converter_kvpairs = yaml.safe_load(stream)

    mappings: dict[str, str] = {}

    for path_converter_dict in path_converter_kvpairs:
        mappings[path_converter_dict["path"]] = path_converter_dict["converter"]

    def get_converter_func(path: Path) -> Converter | None:
        converter_name = mappings.get(str(path))
        return CONVERTER_FUNCS.get(converter_name) if converter_name else None

    return get_converter_func


_converter_map: ConverterMap = default_converter_map
