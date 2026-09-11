import pytest
from tests.constants import TestDataPaths

from daq_config_server.models.i15_1.collection_specification import (
    CollectionSpecification,
    SpecificationPerPosition,
)


def test_collection_spec_parses_lut_contents():
    with open(TestDataPaths.TEST_I15_1_POSITIONS_TIMES_LUT) as f:
        contents = f.read()

    result = CollectionSpecification.from_lut(contents)
    assert result.tth_angle_to_specification == {
        10: SpecificationPerPosition(
            exposure_time=0.05,
            slow_attenuator_transmission=0.01,
            fast_attenuator_position="IN",
        ),
        20: SpecificationPerPosition(
            exposure_time=0.05,
            slow_attenuator_transmission=0.1,
            fast_attenuator_position="IN",
        ),
        30: SpecificationPerPosition(
            exposure_time=0.1,
            slow_attenuator_transmission=1,
            fast_attenuator_position="OUT",
        ),
        40: SpecificationPerPosition(
            exposure_time=0.2,
            slow_attenuator_transmission=10,
            fast_attenuator_position="OUT",
        ),
        50: SpecificationPerPosition(
            exposure_time=0.3,
            slow_attenuator_transmission=50,
            fast_attenuator_position="OUT",
        ),
        60: SpecificationPerPosition(
            exposure_time=0.3,
            slow_attenuator_transmission=100,
            fast_attenuator_position="OUT",
        ),
    }


def test_collection_spec_normalises_times():
    result = CollectionSpecification.model_validate(
        {
            "tth_angle_to_specification": {
                10: {
                    "exposure_time": 1,
                    "slow_attenuator_transmission": 0.01,
                    "fast_attenuator_position": "IN",
                },
                20: {
                    "exposure_time": 1,
                    "slow_attenuator_transmission": 0.01,
                    "fast_attenuator_position": "IN",
                },
                30: {
                    "exposure_time": 2,
                    "slow_attenuator_transmission": 0.01,
                    "fast_attenuator_position": "OUT",
                },
                40: {
                    "exposure_time": 4,
                    "slow_attenuator_transmission": 0.01,
                    "fast_attenuator_position": "OUT",
                },
                50: {
                    "exposure_time": 6,
                    "slow_attenuator_transmission": 0.01,
                    "fast_attenuator_position": "OUT",
                },
                60: {
                    "exposure_time": 6,
                    "slow_attenuator_transmission": 0.01,
                    "fast_attenuator_position": "OUT",
                },
            }
        }
    )

    exposures = [
        spec.exposure_time for spec in result.tth_angle_to_specification.values()
    ]

    assert exposures == pytest.approx([0.05, 0.05, 0.1, 0.2, 0.3, 0.3])  # pyright: ignore[reportUnknownMemberType]
    assert sum(exposures) == 1
