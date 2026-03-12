import pytest

from daq_config_server.models.utils import (
    camel_to_snake_case,
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
