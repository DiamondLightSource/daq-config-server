from daq_config_server.models.feature_settings.feature_settings import (
    BaseFeatureSettings,
    FeatureSettingSources,
)


class I04FeatureSettingsSources(FeatureSettingSources):
    ASSUMED_WAVELENGTH_IN_A = "gda.px.expttable.default.wavelength"
    XRC_UNSCALED_TRANSMISSION_FRAC = "gda.mx.bluesky.i04.xrc.unscaled_transmission_frac"
    XRC_UNSCALED_EXPOSURE_TIME_S = "gda.mx.bluesky.i04.xrc.unscaled_exposure_time_s"


class I04FeatureSettings(BaseFeatureSettings):
    ASSUMED_WAVELENGTH_IN_A: float
    XRC_UNSCALED_TRANSMISSION_FRAC: int
    XRC_UNSCALED_EXPOSURE_TIME_S: float

    @classmethod
    def feature_settings_sources(cls) -> type[I04FeatureSettingsSources]:
        return I04FeatureSettingsSources
