import pytest

from daq_config_server.models.utils import (
    camel_to_snake_case,
    get_units_from_lut,
    remove_comments,
)


def test_remove_comments_works_as_expected():
    input = [
        "This line should not be changed",
        "This should stay   # this should go",
        "#This entire line should go",
        "       # as should this one",
        "#        and this one",
        "",
        "  ",
        "   whitespace should be stripped    ",
    ]
    expected_output = [
        "This line should not be changed",
        "This should stay",
        "whitespace should be stripped",
    ]
    assert remove_comments(input) == expected_output


@pytest.mark.parametrize(
    "camel_case, snake_case",
    [
        ("CamelCase", "camel_case"),
        ("camelCase", "camel_case"),
        ("_Camel_Case", "_camel_case"),
        ("CAMELCASE", "camelcase"),
        ("CAMELCAsE", "camelcas_e"),
    ],
)
def test_camel_to_snake_case_works_as_expected(camel_case: str, snake_case: str):
    assert camel_to_snake_case(camel_case) == snake_case


def test_get_units_from_lut():
    expected_units = ["KeV", "mm"]
    str_input = (
        "#######################\nUnits KeV mm\n5.700		5.4606\n5.760		5.5\n"
    )
    units = get_units_from_lut(str_input, ["eV", "mm"])

    assert units == expected_units


def test_if_no_units_in_lut_get_units_returns_default():
    str_input = (
        "# distance beamY beamX (values from mosflm)\n"
        "150 152.2 166.26\n"
        "800 152.08 160.96\n"
    )
    default_units = ["mm", "mm", "mm"]
    units = get_units_from_lut(str_input, default_units)

    assert units == default_units
