from collections.abc import Callable
from pathlib import Path
from typing import Any

import xmltodict
import yaml

from daq_config_server.app._config import ConverterConfig
from daq_config_server.models import DisplayConfig, beamline_parameters_to_dict
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


def init_converter_map(config: ConverterConfig):
    global _converter_map
    _converter_map = load_converter_map_from_config_file(Path(config.config_file))


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


_converter_map: ConverterMap = lambda _: None  # noqa: E731
