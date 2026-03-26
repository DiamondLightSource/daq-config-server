from pathlib import Path
from typing import Self

import xmltodict

from daq_config_server.models.base_model import ConfigModel


class TemperatureControllerParams(ConfigModel):
    beam_position: float
    safe_position: float
    settle_time: int | None = None
    tolerance: float | None = None
    units: str | None = None
    ramp_units: str | None = None
    use_calibration: bool | None = None
    use_fast_cool: bool | None = None
    calibration_file: str | Path | None = None


class TemperatureControllersConfig(ConfigModel):
    cobra: TemperatureControllerParams
    blower: TemperatureControllerParams
    cryostream: TemperatureControllerParams

    @classmethod
    def from_xpdf_parameters(cls, contents: str) -> Self:
        config_dict = xmltodict.parse(contents)
        cobra = TemperatureControllerParams.model_validate(
            config_dict["configuration"]["devices"]["cobra"]
        )
        blower = TemperatureControllerParams.model_validate(
            config_dict["configuration"]["devices"]["blower"]
        )
        cryostream = TemperatureControllerParams.model_validate(
            config_dict["configuration"]["devices"]["cryostream"]
        )
        return cls(cobra=cobra, blower=blower, cryostream=cryostream)
