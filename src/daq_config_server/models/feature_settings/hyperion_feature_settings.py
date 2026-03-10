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
    # Defaults used if they don't exist in config file
    USE_GPU_RESULTS: bool = True
    USE_PANDA_FOR_GRIDSCAN: bool = False
    SET_STUB_OFFSETS: bool = False
    PANDA_RUNUP_DISTANCE_MM: float = 0.16
    DETECTOR_DISTANCE_LIMIT_MAX_MM: float = 700
    DETECTOR_DISTANCE_LIMIT_MIN_MM: float = 250
    BEAMSTOP_DIODE_CHECK: bool = False

    @staticmethod
    def feature_settings_sources() -> type[HyperionFeatureSettingsSources]:
        return HyperionFeatureSettingsSources
