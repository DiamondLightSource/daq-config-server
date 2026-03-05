import re

import pytest

from daq_config_server.models.lookup_tables import GenericLookupTable, parse_generic_lut
from tests.constants import TestDataPaths


@pytest.fixture
def generic_lookup_table():
    return GenericLookupTable(
        column_names=["detector_distance_mm", "beam_centre_x_mm", "beam_centre_y_mm"],
        rows=[[150, 152.2, 166.26], [800, 152.08, 160.96]],
    )


def test_parse_lut_to_dict_gives_expected_result_and_can_be_jsonified():
    with open(TestDataPaths.TEST_GOOD_LUT_PATH) as f:
        contents = f.read()
    expected = GenericLookupTable(
        column_names=["energy_eV", "gap_mm"],
        rows=[[5700, 5.4606], [5760, 5.5], [6000, 5.681], [6500, 6.045]],
    )
    result = parse_generic_lut(contents, ("energy_eV", int), ("gap_mm", float))
    assert result == expected
    result.model_dump_json()


def test_parsing_bad_lut_causes_error():
    with open(TestDataPaths.TEST_BAD_LUT_PATH) as f:
        contents = f.read()
    with pytest.raises(IndexError):
        parse_generic_lut(contents, ("energy_eV", int), ("gap_mm", float))


def test_lut_with_different_number_of_row_items_to_column_names_causes_error():
    with pytest.raises(ValueError, match=" does not match number of columns:"):
        GenericLookupTable(
            column_names=["column1", "column2"], rows=[[1, 2], [1, 2, 3]]
        )


@pytest.mark.parametrize(
    "args, expected_value",
    [
        (("detector_distance_mm", 150, "beam_centre_x_mm", True), 152.2),
        (("beam_centre_y_mm", 160.96, "detector_distance_mm", True), 800),
        (
            ("beam_centre_x_mm", 153, "beam_centre_y_mm", False),
            166.26,  # get closest value when value_must_exist == False
        ),
    ],
)
def test_lut_model_get_value(
    generic_lookup_table: GenericLookupTable,
    args: tuple[str, int | float, str, bool],
    expected_value: int | float,
):
    assert generic_lookup_table.get_value(*args) == expected_value


def test_lut_model_get_value_errors_if_value_doesnt_exist(
    generic_lookup_table: GenericLookupTable,
):
    with pytest.raises(
        ValueError,
        match=re.escape(
            "'160.97' doesn't exist in column 'beam_centre_y_mm': [166.26, 160.96]"
        ),
    ):
        # value doesn't exist
        generic_lookup_table.get_value(
            "beam_centre_y_mm", 160.97, "detector_distance_mm"
        )


def test_lut_model_columns_property(generic_lookup_table: GenericLookupTable):
    expected_columns = [[150, 800], [152.2, 152.08], [166.26, 160.96]]
    assert generic_lookup_table.columns == expected_columns


def test_get_column(generic_lookup_table: GenericLookupTable):
    assert generic_lookup_table.get_column("detector_distance_mm") == [150, 800]
    assert generic_lookup_table.get_column("beam_centre_x_mm") == [152.2, 152.08]
    assert generic_lookup_table.get_column("beam_centre_y_mm") == [166.26, 160.96]


def test_get_column_with_invalid_column_name(generic_lookup_table: GenericLookupTable):
    with pytest.raises(
        ValueError,
        match=re.escape(
            "'column_name' not in column names: "
            + "['detector_distance_mm', 'beam_centre_x_mm', 'beam_centre_y_mm']",
        ),
    ):
        generic_lookup_table.get_column("column_name")
