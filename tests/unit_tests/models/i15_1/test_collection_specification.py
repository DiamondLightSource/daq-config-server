import pytest
from pydantic import ValidationError
from tests.constants import TestDataPaths

from daq_config_server.models.i15_1.collection_specification import (
    CollectionSpecification,
    SpecificationPerPosition,
)


def test_collection_spec_parses_json_contents():
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


def test_collection_spec_normalises_times():
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

    assert exposures == pytest.approx([0.05, 0.05, 0.1, 0.2, 0.3, 0.3])  # pyright: ignore[reportUnknownMemberType]
    assert sum(exposures) == 1
