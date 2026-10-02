from functools import cached_property
from typing import Literal, Self, get_args

import numpy as np
from pydantic import BaseModel

from daq_config_server.models.lookup_tables.generic_lut_models import LookupTableBase
from daq_config_server.models.utils import parse_and_cast_lut_rows

TEMPERATURE_CALIBRATION_COLUMN_NAMES = Literal["setpoint", "negative_error"]


class ThirdOrderPolynomial(BaseModel):
    # From highest order to lowest
    coefficients: tuple[float, float, float, float]

    def calc(self, value: float) -> float:
        return float(np.polyval(self.coefficients, value))


class TemperatureCalibration(LookupTableBase[TEMPERATURE_CALIBRATION_COLUMN_NAMES]):
    def get_column_names(self) -> list[TEMPERATURE_CALIBRATION_COLUMN_NAMES]:
        return list(get_args(TEMPERATURE_CALIBRATION_COLUMN_NAMES))

    @classmethod
    def from_contents(cls, contents: str) -> Self:
        rows = parse_and_cast_lut_rows(contents, [float, float])
        return cls(rows=rows)

    @cached_property
    def polynomial(self) -> ThirdOrderPolynomial:
        setpoints = np.array(self.columns[0])
        actual_temps = setpoints - np.array(self.columns[1])
        coefficients = tuple(np.polyfit(actual_temps, setpoints, deg=3))
        return ThirdOrderPolynomial(coefficients=coefficients)
