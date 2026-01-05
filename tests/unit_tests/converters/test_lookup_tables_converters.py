import re

import pytest
from tests.constants import TestDataPaths

from daq_config_server.models.converters.lookup_tables import (
    DetectorXYLookupTable,
    GenericLookupTable,
    beamline_pitch_lut,
    beamline_roll_lut,
    detector_xy_lut,
    i09_hu_undulator_energy_gap_lut,
    undulator_energy_gap_lut,
)
from daq_config_server.models.converters.lookup_tables._converters import parse_lut


def test_parse_lut_to_dict_gives_expected_result_and_can_be_jsonified():
    with open(TestDataPaths.TEST_GOOD_LUT_PATH) as f:
        contents = f.read()
    expected = GenericLookupTable(
        column_names=["energy_eV", "gap_mm"],
        rows=[[5700, 5.4606], [5760, 5.5], [6000, 5.681], [6500, 6.045]],
    )
    result = parse_lut(contents, ("energy_eV", int), ("gap_mm", float))
    assert result == expected
    result.model_dump_json()


def test_parsing_bad_lut_causes_error():
    with open(TestDataPaths.TEST_BAD_LUT_PATH) as f:
        contents = f.read()
    with pytest.raises(IndexError):
        parse_lut(contents, ("energy_eV", int), ("gap_mm", float))


def test_lut_with_different_number_of_row_items_to_column_names_causes_error():
    with pytest.raises(ValueError, match=" does not match number of columns:"):
        GenericLookupTable(
            column_names=["column1", "column2"], rows=[[1, 2], [1, 2, 3]]
        )


def test_detector_xy_lut_gives_expected_results():
    input = (
        "# distance beamY beamX (values from mosflm)\n"
        "Units mm mm mm\n"
        "150 152.2 166.26\n"
        "800 152.08 160.96\n"
    )
    expected = GenericLookupTable(
        column_names=["detector_distances_mm", "beam_centre_x_mm", "beam_centre_y_mm"],
        rows=[[150, 152.2, 166.26], [800, 152.08, 160.96]],
    )
    result = detector_xy_lut(input)
    assert result == expected


def test_beamline_pitch_lut_gives_expected_result():
    input = (
        "#       Bragg	pitch\n"
        "#	Degree	values	for	pitch	are	interpreted	as	mrad\n"
        "#	The	values	cannot	change	direction.\n"
        "#       last update 2025/01/15 NP\n"
        "Units Deg mrad\n"
        "Units Deg Deg\n"
        "16.40956 -0.62681\n"
        "14.31123 -0.61833\n"
        "12.69285 -0.61243\n"
        "11.40557 -0.60849\n"
    )
    expected = GenericLookupTable(
        column_names=["bragg_angle_deg", "pitch_mrad"],
        rows=[
            [16.40956, -0.62681],
            [14.31123, -0.61833],
            [12.69285, -0.61243],
            [11.40557, -0.60849],
        ],
    )
    result = beamline_pitch_lut(input)
    assert result == expected


def test_beamline_roll_lut_gives_expected_result():
    input = (
        "#Bragg angle against roll( absolute number)\n"
        "#reloadLookupTables()\n"
        "# last update 2024/06/20 NP\n"
        "Units Deg mrad\n"
        "26.4095 2.6154\n"
        "6.3075  2.6154\n"
    )
    expected = GenericLookupTable(
        column_names=["bragg_angle_deg", "roll_mrad"],
        rows=[[26.4095, 2.6154], [6.3075, 2.6154]],
    )
    result = beamline_roll_lut(input)
    assert result == expected


def test_undulator_gap_lut_gives_expected_result():
    input = (
        "#######################\n"
        "#                     #\n"
        "# 5.5mm CPMU 20/11/22 #\n"
        "#                     #\n"
        "Units eV mm\n"
        "5700		5.4606\n"
        "5760		5.5\n"
        "6000		5.681\n"
        "6500		6.045\n"
    )
    expected = GenericLookupTable(
        column_names=["energy_eV", "gap_mm"],
        rows=[[5700, 5.4606], [5760, 5.5], [6000, 5.681], [6500, 6.045]],
    )
    result = undulator_energy_gap_lut(input)
    assert result == expected


def test_i09_hu_undulator_gap_lut_gives_expected_result():
    input = (
        "#I09 Hard X-ray ID calibration parameters, created 18 July 2012\n"
        "ScannableNames	n	Ee	Br	Epmin	Epmax	Gmin	Gmax	Goffset\n"
        "ScannableUnits	ONE	GeV	T	KeV	Kev	mm	mm\n"
        "1	3.00089	0.98928	2.12	3.05	14.2650	23.7200	0.0\n"
        "2	3.04129	1.02504	2.50	2.80	5.05165	8.88007	0.0\n"
    )
    expected = GenericLookupTable(
        column_names=[
            "order",
            "ring_energy_gev",
            "magnetic_field_t",
            "energy_min_ev",
            "energy_max_ev",
            "gap_min_mm",
            "gap_max_mm",
            "gap_offset_mm",
        ],
        rows=[
            [1, 3.00089, 0.98928, 2.12, 3.05, 14.2650, 23.7200, 0.0],
            [2, 3.04129, 1.02504, 2.50, 2.80, 5.05165, 8.88007, 0.0],
        ],
    )
    result = i09_hu_undulator_energy_gap_lut(input)
    assert result == expected


@pytest.mark.parametrize(
    "args, expected_value",
    [
        (("detector_distances_mm", 150, "beam_centre_x_mm", True), 152.2),
        (("beam_centre_y_mm", 160.96, "detector_distances_mm", True), 800),
        (
            ("beam_centre_x_mm", 153, "beam_centre_y_mm", False),
            166.26,  # get closest value when value_must_exist == False
        ),
    ],
)
def test_generic_lut_model_get_value_function(
    args: tuple[str, int | float, str, bool], expected_value: int | float
):
    my_lut = GenericLookupTable(
        column_names=["detector_distances_mm", "beam_centre_x_mm", "beam_centre_y_mm"],
        rows=[[150, 152.2, 166.26], [800, 152.08, 160.96]],
    )
    assert my_lut.get_value(*args) == expected_value


def test_generic_lut_model_get_value_errors_if_value_doesnt_exist():
    my_lut = GenericLookupTable(
        column_names=["detector_distances_mm", "beam_centre_x_mm", "beam_centre_y_mm"],
        rows=[[150, 152.2, 166.26], [800, 152.08, 160.96]],
    )
    with pytest.raises(
        ValueError,
        match=re.escape(
            "'160.97' doesn't exist in column 'beam_centre_y_mm': [166.26, 160.96]"
        ),
    ):
        # value doesn't exist
        my_lut.get_value("beam_centre_y_mm", 160.97, "detector_distances_mm")


def test_generic_lut_model_columns_function():
    my_lut = GenericLookupTable(
        column_names=["detector_distances_mm", "beam_centre_x_mm", "beam_centre_y_mm"],
        rows=[[150, 152.2, 166.26], [800, 152.08, 160.96]],
    )
    expected_columns = [[150, 800], [152.2, 152.08], [166.26, 160.96]]
    assert my_lut.columns() == expected_columns


def test_detector_xy_lut_model_column_names():
    my_lut = DetectorXYLookupTable(rows=[[1, 2, 3]])
    assert my_lut.get_column_names() == [
        "detector_distances_mm",
        "beam_centre_x_mm",
        "beam_centre_y_mm",
    ]


def test_detector_xy_lut_model_get_value():
    my_lut = DetectorXYLookupTable(
        rows=[[1.1, 2.2, 3.3], [4.4, 5.5, 6.6]],
    )
    assert my_lut.get_value("beam_centre_x_mm", 5.5, "beam_centre_y_mm") == 6.6
