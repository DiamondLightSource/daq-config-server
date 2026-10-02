import pytest
from pydantic import ValidationError

from daq_config_server.models.i15_1.standards_puck import StandardsPin, StandardsPuck

from .conftest import TestI151DataPaths


def test_standards_puck_json_is_read_correctly():
    with open(TestI151DataPaths.STANDARDS_PUCK) as f:
        contents = f.read()
    expected = StandardsPuck(
        position_on_table=1,
        pins={
            1: StandardsPin(capillary="metal", contents=None),
            2: StandardsPin(capillary="bs1.0", contents="Silicon"),
            3: StandardsPin(capillary="fq1.0", contents="Silicon"),
            4: StandardsPin(capillary="bs1.5", contents="Silicon"),
            5: None,
            6: StandardsPin(capillary="bs2.0", contents="Silicon"),
            7: None,
            8: None,
            9: StandardsPin(capillary="bs1.0", contents="Si/Al2O3"),
            10: StandardsPin(capillary="fq1.0", contents="Si/Al2O3"),
            11: StandardsPin(capillary="fq1.5", contents="Si/Al2O3"),
            12: StandardsPin(capillary="fq2.0", contents="Si/Al2O3"),
            13: StandardsPin(capillary="bs1.0", contents="Pb"),
            14: StandardsPin(capillary="bs1.0", contents="LaB6 660b"),
            15: StandardsPin(capillary="bs1.0", contents=None),
            16: StandardsPin(capillary="fq1.0", contents=None),
            17: StandardsPin(capillary="bs1.5", contents=None),
            18: StandardsPin(capillary="fq1.5", contents=None),
            19: StandardsPin(capillary="bs2.0", contents=None),
            20: StandardsPin(capillary="fq2.0", contents=None),
            21: StandardsPin(capillary="bs1.0", contents="Ga/In"),
            22: StandardsPin(capillary="bs1.0", contents="Tungsten/Boron mix"),
        },
    )
    result = StandardsPuck.model_validate_json(contents)
    assert result == expected


@pytest.mark.parametrize(
    "pins",
    [
        {},
        {1: None, 22: None},
        {  # Check when more pins defined than expected
            1: None,
            2: None,
            3: None,
            4: None,
            5: None,
            6: None,
            7: None,
            8: None,
            9: None,
            10: None,
            11: None,
            12: None,
            13: None,
            14: None,
            15: None,
            16: None,
            17: None,
            18: None,
            19: None,
            20: None,
            21: None,
            22: None,
            23: None,
        },
    ],
)
def test_if_wrong_pin_numbers_parsed_then_error_raised(
    pins: dict[int, StandardsPin | None],
):
    with pytest.raises(ValidationError):
        StandardsPuck(position_on_table=1, pins=pins)


def test_standards_puck_get_pin_number_works_as_expected():
    with open(TestI151DataPaths.STANDARDS_PUCK) as f:
        contents = f.read()

    standards = StandardsPuck.model_validate_json(contents)
    assert (
        standards.get_position_of_pin(
            StandardsPin(capillary="bs1.5", contents="Silicon")
        )
        == 4
    )


def test_standards_puck_get_pin_number_raises_if_no_matching_pin_exists():
    with open(TestI151DataPaths.STANDARDS_PUCK) as f:
        contents = f.read()

    standards = StandardsPuck.model_validate_json(contents)
    with pytest.raises(ValueError):
        standards.get_position_of_pin(
            StandardsPin(capillary="bs1.5", contents="Tungsten/Boron mix")
        )
