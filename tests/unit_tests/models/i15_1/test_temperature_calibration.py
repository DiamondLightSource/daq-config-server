import pytest

from daq_config_server.models.i15_1.temperature_calibration import (
    TemperatureCalibration,
    ThirdOrderPolynomial,
)
from tests.unit_tests.models.i15_1.conftest import TestI151DataPaths


@pytest.fixture
def temperature_calibration():
    with open(TestI151DataPaths.TEMPERATURE_CALIBRATION) as f:
        contents = f.read()
    return TemperatureCalibration.from_contents(contents)


def test_temperature_calibration_is_read_correctly(
    temperature_calibration: TemperatureCalibration,
):
    assert temperature_calibration.model_dump() == {
        "rows": [
            [50.0, 0.62034],
            [100.0, 16.89903],
            [150.0, 26.49641],
            [200.0, 33.91664],
            [250.0, 47.85712],
            [300.0, 62.41245],
            [350.0, 80.13215],
            [400.0, 96.91991],
            [450.0, 115.6384],
            [500.0, 135.89034],
            [550.0, 155.75917],
        ]
    }


def test_temperature_calibration_produces_expected_polynomials(
    temperature_calibration: TemperatureCalibration,
):
    assert temperature_calibration.real_to_setpoint == ThirdOrderPolynomial(
        coefficients=(
            1.3632771786784797e-06,
            -0.00012637763892189705,
            1.2595608567266499,
            -8.87384936825852,
        )
    )
    assert temperature_calibration.setpoint_to_real == ThirdOrderPolynomial(
        coefficients=(
            -1.214726184926246e-07,
            -0.00015139577622377191,
            0.824064798795648,
            5.972881969696991,
        )
    )


def test_polynomial_calculates_required_setpoint_for_a_desired_temperature(
    temperature_calibration: TemperatureCalibration,
):
    for setpoint, negative_error in zip(
        temperature_calibration.columns[0],
        temperature_calibration.columns[1],
        strict=True,
    ):
        assert temperature_calibration.real_to_setpoint.calc(
            setpoint - negative_error
        ) == pytest.approx(setpoint, abs=5)  # type: ignore

    assert temperature_calibration.real_to_setpoint.calc(500) == 759.721816599402


def test_polynomial_calculates_real_temperature_from_setpoint(
    temperature_calibration: TemperatureCalibration,
):
    for setpoint, negative_error in zip(
        temperature_calibration.columns[0],
        temperature_calibration.columns[1],
        strict=True,
    ):
        assert temperature_calibration.setpoint_to_real.calc(setpoint) == pytest.approx(  # type: ignore
            setpoint - negative_error, abs=5
        )

    assert temperature_calibration.setpoint_to_real.calc(759.7) == 491.37728934391555
