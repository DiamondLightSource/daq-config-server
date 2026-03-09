from daq_config_server.models.feature_settings.hyperion_feature_settings import (
    HyperionFeatureSettings,
)
from daq_config_server.models.feature_settings.i04_feature_settings import (
    I04FeatureSettings,
)
from tests.constants import TestDataPaths


def test_hyperion_feature_flags():
    with open(TestDataPaths.TEST_HYPERION_DOMAIN_PROPERTIES) as f:
        contents = f.read()
    expected = HyperionFeatureSettings(
        USE_GPU_RESULTS=True,
        USE_PANDA_FOR_GRIDSCAN=True,
        SET_STUB_OFFSETS=False,
        PANDA_RUNUP_DISTANCE_MM=0.16,
        DETECTOR_DISTANCE_LIMIT_MAX_MM=800.0,
        DETECTOR_DISTANCE_LIMIT_MIN_MM=150.0,
        BEAMSTOP_DIODE_CHECK=False,
    )
    config = HyperionFeatureSettings.from_contents(contents)
    assert config == expected


def test_i04_feature_flags():
    with open(TestDataPaths.TEST_I04_DOMAIN_PROPERTIES) as f:
        contents = f.read()
    expected = I04FeatureSettings(
        ASSUMED_WAVELENGTH_IN_A=0.95373,
        XRC_UNSCALED_TRANSMISSION_FRAC=1,
        XRC_UNSCALED_EXPOSURE_TIME_S=0.007,
    )
    config = I04FeatureSettings.from_contents(contents)
    assert config == expected
