import pytest
from tests.constants import TestDataPaths

from daq_config_server.converters.lookup_tables._converters import (
    beamline_pitch_lut,
    beamline_roll_lut,
    detector_xy_lut,
    parse_lut,
    undulator_energy_gap_lut,
)
from daq_config_server.models import GenericLookupTable


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
