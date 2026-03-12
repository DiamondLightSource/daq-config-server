import pytest
from pydantic import ValidationError

from daq_config_server.models.feature_settings.feature_settings import (
    BaseFeatureSettings,
    FeatureSettingSources,
)
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
    config = HyperionFeatureSettings.from_domain_properties(contents)
    assert config == expected


def test_i04_feature_flags():
    with open(TestDataPaths.TEST_I04_DOMAIN_PROPERTIES) as f:
        contents = f.read()
    expected = I04FeatureSettings(
        ASSUMED_WAVELENGTH_IN_A=0.95373,
        XRC_UNSCALED_TRANSMISSION_FRAC=1,
        XRC_UNSCALED_EXPOSURE_TIME_S=0.007,
    )
    config = I04FeatureSettings.from_domain_properties(contents)
    assert config == expected


def test_error_raised_when_feature_settings_class_doesnt_match_source_class():
    class BadFeatureSettingsSources(FeatureSettingSources):
        USE_GPU_RESULTS = "gda.mx.hyperion.xrc.use_gpu_results"
        USE_ZEBRA_FOR_GRIDSCAN = "gda.mx.hyperion.use_panda_for_gridscans"
        SET_STUB_OFFSETS = "gda.mx.hyperion.do_stub_offsets"

    class BadFeatureSettings(BaseFeatureSettings):
        USE_GPU_RESULTS: bool = False

        @staticmethod
        def feature_settings_sources():
            return BadFeatureSettingsSources

    with pytest.raises(ValidationError):
        BadFeatureSettings.from_domain_properties("")

    with pytest.raises(ValidationError):
        BadFeatureSettings(USE_GPU_RESULTS=True)


def test_warning_logged_when_fields_missing_in_source_file(
    caplog: pytest.LogCaptureFixture,
):
    caplog.set_level("WARNING")
    I04FeatureSettings.from_domain_properties("")
    expected_messages = [
        "Could not find gda.px.expttable.default.wavelength",
        "Could not find gda.mx.bluesky.i04.xrc.unscaled_transmission_frac",
        "Could not find gda.mx.bluesky.i04.xrc.unscaled_exposure_time_s",
    ]
    assert all(
        any(expected_message in message for message in caplog.messages)
        for expected_message in expected_messages
    )
