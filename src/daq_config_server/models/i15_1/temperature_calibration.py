from functools import cached_property
from typing import Literal, Self, TypeAlias, get_args

import numpy as np
from pydantic import BaseModel, field_validator, model_validator

from daq_config_server.models.lookup_tables.generic_lut_models import LookupTableBase
from daq_config_server.models.utils import parse_and_cast_lut_rows

TEMPERATURE_CALIBRATION_COLUMN_NAMES = Literal["setpoint", "negative_error"]

Coefficients: TypeAlias = tuple[float, float, float, float]


class ThirdOrderMonotonicPolynomial(BaseModel):
    # From highest order to lowest
    coefficients: Coefficients

    def calc(self, value: float) -> float:
        return float(np.polyval(self.coefficients, value))

    def inverse_calc(self, value: float) -> float:
        a, b, c, d = self.coefficients
        roots = np.roots([a, b, c, d - value])
        real_roots = roots[np.isclose(roots.imag, 0)].real
        assert len(real_roots) == 1, f"More than one root found: {real_roots}"
        return float(real_roots[0])

    @field_validator("coefficients", mode="after")
    @classmethod
    def must_be_monotonic_and_increasing(
        cls, coefficients: Coefficients
    ) -> Coefficients:
        a, b, c, _ = coefficients
        assert a > 0 and b * b <= 3 * a * c, (
            "The polynomial fit is not monotonically increasing."
        )
        return coefficients


class TemperatureCalibration(LookupTableBase[TEMPERATURE_CALIBRATION_COLUMN_NAMES]):
    def get_column_names(self) -> list[TEMPERATURE_CALIBRATION_COLUMN_NAMES]:
        return list(get_args(TEMPERATURE_CALIBRATION_COLUMN_NAMES))

    @classmethod
    def from_contents(cls, contents: str) -> Self:
        rows = parse_and_cast_lut_rows(contents, [float, float])
        return cls(rows=rows)

    @cached_property
    def real_to_setpoint(self) -> ThirdOrderMonotonicPolynomial:
        setpoints = np.array(self.columns[0])
        actual_temps = setpoints - np.array(self.columns[1])
        coefficients = tuple(np.polyfit(actual_temps, setpoints, deg=3))
        return ThirdOrderMonotonicPolynomial(coefficients=coefficients)

    @model_validator(mode="after")
    def check_polynomial_can_be_created(self):
        _ = self.real_to_setpoint
        return self
