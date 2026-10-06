import pytest

from daq_config_server.models.i15_1.temperature_calibration import (
    TemperatureCalibration,
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
        ],
        "real_to_setpoint": {
            "coefficients": pytest.approx(  # type: ignore
                (
                    1.3632771786784797e-06,
                    -0.00012637763892189705,
                    1.2595608567266499,
                    -8.87384936825852,
                )
            )
        },
    }


def test_temperature_calibration_can_be_serialised_and_desrialised(
    temperature_calibration: TemperatureCalibration,
):
    serialised = temperature_calibration.model_dump()
    TemperatureCalibration.model_validate(serialised)


def test_temperature_calibration_produces_expected_polynomials(
    temperature_calibration: TemperatureCalibration,
):
    assert temperature_calibration.real_to_setpoint.coefficients == pytest.approx(  # type: ignore
        (
            1.3632771786784797e-06,
            -0.00012637763892189705,
            1.2595608567266499,
            -8.87384936825852,
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

    assert temperature_calibration.real_to_setpoint.calc(500) == pytest.approx(  # type: ignore
        759.721816599402
    )


def test_polynomial_calculates_real_temperature_from_setpoint(
    temperature_calibration: TemperatureCalibration,
):
    for setpoint, negative_error in zip(
        temperature_calibration.columns[0],
        temperature_calibration.columns[1],
        strict=True,
    ):
        assert temperature_calibration.real_to_setpoint.inverse_calc(
            setpoint
        ) == pytest.approx(setpoint - negative_error, abs=5)  # type: ignore

    assert temperature_calibration.real_to_setpoint.inverse_calc(
        759.721816599402
    ) == pytest.approx(500)  # type: ignore


def test_polynomial_raises_error_if_not_monotonically_increasing():
    with pytest.raises(ValueError):
        TemperatureCalibration(
            rows=[
                [50.0, 0.62034],
                [100.0, 16.89903],
                [150.0, 26.49641],
                [200.0, 33.91664],
                [250.0, -10],
                [300.0, -20],
                [350.0, -50],
                [400.0, 96.91991],
                [450.0, 115.6384],
                [500.0, 135.89034],
                [550.0, 155.75917],
            ]
        )
