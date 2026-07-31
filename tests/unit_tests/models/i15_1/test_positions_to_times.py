import pytest
from tests.constants import TestDataPaths

from daq_config_server.models.i15_1.positions_to_times import AnglesToTimes


def test_positions_to_times_parses_json_contents():
    with open(TestDataPaths.TEST_I15_1_POSITIONS_TIMES_LUT) as f:
        contents = f.read()

    result = AnglesToTimes.from_lut(contents)
    assert result.tth_angle_to_collection_time == {
        10: 0.05,
        20: 0.05,
        30: 0.1,
        40: 0.2,
        50: 0.3,
        60: 0.3,
    }


def test_positions_to_times_normalises_times():
    result = AnglesToTimes(
        tth_angle_to_collection_time={
            10: 1,
            20: 1,
            30: 2,
            40: 4,
            50: 6,
            60: 6,
        }
    )

    assert result.tth_angle_to_collection_time == pytest.approx(  # type: ignore
        {
            10: 0.05,
            20: 0.05,
            30: 0.1,
            40: 0.2,
            50: 0.3,
            60: 0.3,
        }
    )
    assert sum(result.tth_angle_to_collection_time.values()) == 1
