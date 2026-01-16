from typing import Any

import pytest

from daq_config_server.models.converters import (
    camel_to_snake_case,
    parse_value,
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
    "value, convert_to, expected_parsed_value",
    [
        ("  2.0   ", None, 2.0),
        (" 3 ", None, 3),
        ("5.0", float, 5.0),
        ("5.0", int, 5),
    ],
)
def test_parse_value_works_as_expected(
    value: str, convert_to: type, expected_parsed_value: Any
):
    parsed_value = parse_value(value, convert_to)
    assert parsed_value == expected_parsed_value
    assert type(parsed_value) is type(expected_parsed_value)


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
