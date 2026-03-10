from daq_config_server.models.feature_settings.feature_settings import (
    BaseFeatureSettings,
    FeatureSettingSources,
)


class I04FeatureSettingsSources(FeatureSettingSources):
    ASSUMED_WAVELENGTH_IN_A = "gda.px.expttable.default.wavelength"
    XRC_UNSCALED_TRANSMISSION_FRAC = "gda.mx.bluesky.i04.xrc.unscaled_transmission_frac"
    XRC_UNSCALED_EXPOSURE_TIME_S = "gda.mx.bluesky.i04.xrc.unscaled_exposure_time_s"


class I04FeatureSettings(BaseFeatureSettings):
    # Defaults used if they don't exist in config file
    ASSUMED_WAVELENGTH_IN_A: float = 0.95373
    XRC_UNSCALED_TRANSMISSION_FRAC: int = 1
    XRC_UNSCALED_EXPOSURE_TIME_S: float = 0.007

    @staticmethod
    def feature_settings_sources() -> type[I04FeatureSettingsSources]:
        return I04FeatureSettingsSources
