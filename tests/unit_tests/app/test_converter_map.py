from pathlib import Path

import pytest

from daq_config_server.app._config import ConverterConfig
from daq_config_server.app._file_converter_map import (
    ConverterMap,
    get_converter,
    init_converter_map,
    load_converter_map_from_config_file,
)
from daq_config_server.models import DisplayConfig
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
    GenericLookupTable,
)
from daq_config_server.models.lookup_tables.insertion_device import (
    UndulatorEnergyGapLookupTable,
)


@pytest.fixture(autouse=True)
def converter_map_from_config():
    return load_converter_map_from_config_file(
        Path("tests/test_data/test_converter_map.yaml")
    )


@pytest.mark.parametrize(
    "path_str, expected_type",
    [
        ["tests/test_data/test_good_lut.txt", UndulatorEnergyGapLookupTable],
        ["tests/test_data/test_display.configuration", DisplayConfig],
        ["tests/test_data/beamline_parameters.txt", dict],
        ["tests/test_data/test_xml.xml", dict],
        ["tests/test_data/test_i04_domain.properties", I04FeatureSettings],
        ["tests/test_data/test_hyperion_domain.properties", HyperionFeatureSettings],
        ["tests/test_data/test_xpdfLocalParameters.xml", TemperatureControllersConfig],
        ["tests/test_data/test_good_detector_xy_lut.txt", DetectorXYLookupTable],
        ["tests/test_data/test_good_beamline_pitch_lut.txt", BeamlinePitchLookupTable],
        ["tests/test_data/test_good_beamline_roll_lut.txt", BeamlineRollLookupTable],
        ["tests/test_data/test_good_i09_hu_undulator_gap_lut.txt", GenericLookupTable],
    ],
)
def test_filesystem_converter_map_maps_all_files_target_type(
    path_str: str, expected_type: type, converter_map_from_config: ConverterMap
):
    path = Path(path_str)
    with path.open() as stream:
        content = stream.read()
        converted = converter_map_from_config(path)(content)  # type: ignore
    assert isinstance(converted, expected_type)


def test_filesystem_converter_map_returns_none_for_unmapped_file(
    converter_map_from_config: ConverterMap,
):
    assert converter_map_from_config(Path("/this/path/does/not/exist")) is None


def test_init_converter_map_updates_converter():
    initial_conversion = get_converter(Path("tests/test_data/test_xml.xml"))
    assert initial_conversion is None
    init_converter_map(
        ConverterConfig(config_file="tests/test_data/test_converter_map.yaml")
    )
    new_conversion = get_converter(Path("tests/test_data/test_xml.xml"))
    assert callable(new_conversion)

    init_converter_map(ConverterConfig())
    assert get_converter(Path("tests/test_data/test_xml.xml")) is None
