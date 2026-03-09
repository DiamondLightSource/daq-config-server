from daq_config_server.models.feature_settings.feature_settings import (
    BaseFeatureSettings,
    FeatureSettingSources,
)


class HyperionFeatureSettingsSources(FeatureSettingSources):
    USE_GPU_RESULTS = "gda.mx.hyperion.xrc.use_gpu_results"
    USE_PANDA_FOR_GRIDSCAN = "gda.mx.hyperion.use_panda_for_gridscans"
    SET_STUB_OFFSETS = "gda.mx.hyperion.do_stub_offsets"
    PANDA_RUNUP_DISTANCE_MM = "gda.mx.hyperion.panda_runup_distance_mm"
    DETECTOR_DISTANCE_LIMIT_MAX_MM = "gda.detector.distance.limit.max"
    DETECTOR_DISTANCE_LIMIT_MIN_MM = "gda.detector.distance.limit.min"
    BEAMSTOP_DIODE_CHECK = "gda.mx.hyperion.enable_beamstop_diode_check"


class HyperionFeatureSettings(BaseFeatureSettings):
    USE_GPU_RESULTS: bool
    USE_PANDA_FOR_GRIDSCAN: bool
    SET_STUB_OFFSETS: bool
    PANDA_RUNUP_DISTANCE_MM: float
    DETECTOR_DISTANCE_LIMIT_MAX_MM: float
    DETECTOR_DISTANCE_LIMIT_MIN_MM: float
    BEAMSTOP_DIODE_CHECK: bool = False

    @classmethod
    def feature_settings_sources(cls):
        return HyperionFeatureSettingsSources
