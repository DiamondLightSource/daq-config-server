from daq_config_server.models.lookup_tables.mx import (
    BeamlinePitchLookupTable,
    BeamlineRollLookupTable,
    DetectorXYLookupTable,
)


def test_detector_xy_lut_gives_expected_results():
    input = (
        "# distance beamY beamX (values from mosflm)\n"
        "Units mm mm mm\n"
        "150 152.2 166.26\n"
        "800 152.08 160.96\n"
    )
    expected = DetectorXYLookupTable(
        rows=[[150, 152.2, 166.26], [800, 152.08, 160.96]],
    )
    result = DetectorXYLookupTable.from_contents(input)
    assert result == expected
    assert result.get_column_names() == [
        "detector_distance_mm",
        "beam_centre_x_mm",
        "beam_centre_y_mm",
    ]


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
    expected = BeamlinePitchLookupTable(
        rows=[
            [16.40956, -0.62681],
            [14.31123, -0.61833],
            [12.69285, -0.61243],
            [11.40557, -0.60849],
        ],
    )
    result = BeamlinePitchLookupTable.from_contents(input)
    assert result == expected
    assert result.get_column_names() == ["bragg_angle_deg", "pitch_mrad"]


def test_beamline_roll_lut_gives_expected_result():
    input = (
        "#Bragg angle against roll( absolute number)\n"
        "#reloadLookupTables()\n"
        "# last update 2024/06/20 NP\n"
        "Units Deg mrad\n"
        "26.4095 2.6154\n"
        "6.3075  2.6154\n"
    )
    expected = BeamlineRollLookupTable(rows=[[26.4095, 2.6154], [6.3075, 2.6154]])
    result = BeamlineRollLookupTable.from_contents(input)
    assert result == expected
    assert result.get_column_names() == ["bragg_angle_deg", "roll_mrad"]
