import pytest
from pydantic import ValidationError
from tests.constants import TestDataPaths

from daq_config_server.models.i15_1.positions_to_times import (
    CollectionSpecification,
    SpecificationPerPosition,
)


def test_positions_to_times_parses_json_contents():
    with open(TestDataPaths.TEST_I15_1_POSITIONS_TIMES_LUT) as f:
        contents = f.read()

    result = CollectionSpecification.from_lut(contents)
    assert result.tth_angle_to_specification == {
        10: SpecificationPerPosition(exposure_time=0.05, transmission=0.01),
        20: SpecificationPerPosition(exposure_time=0.05, transmission=0.1),
        30: SpecificationPerPosition(exposure_time=0.1, transmission=1),
        40: SpecificationPerPosition(exposure_time=0.2, transmission=10),
        50: SpecificationPerPosition(exposure_time=0.3, transmission=50),
        60: SpecificationPerPosition(exposure_time=0.3, transmission=100),
    }


def test_positions_to_times_normalises_times():
    result = CollectionSpecification.model_validate(
        {
            "tth_angle_to_specification": {
                10: {"exposure_time": 1, "transmission": 0.01},
                20: {"exposure_time": 1, "transmission": 0.01},
                30: {"exposure_time": 2, "transmission": 0.01},
                40: {"exposure_time": 4, "transmission": 0.01},
                50: {"exposure_time": 6, "transmission": 0.01},
                60: {"exposure_time": 6, "transmission": 0.01},
            }
        }
    )

    exposures = [
        spec.exposure_time for spec in result.tth_angle_to_specification.values()
    ]

    assert exposures == pytest.approx([0.05, 0.05, 0.1, 0.2, 0.3, 0.3])
    assert sum(exposures) == 1


@pytest.mark.parametrize("transmission", [2, 0.02, 0.0001, 101])
def test_positions_to_times_rejects_invalid_transmission(transmission: float):
    with pytest.raises(ValidationError):
        SpecificationPerPosition(exposure_time=1, transmission=transmission)
