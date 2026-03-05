from daq_config_server.models.lookup_tables import GenericLookupTable
from daq_config_server.models.lookup_tables.insertion_device.hard import (
    UndulatorEnergyGapLookupTable,
    parse_i09_hu_undulator_energy_gap_lut,
)


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
    result = parse_i09_hu_undulator_energy_gap_lut(input)
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
    expected = UndulatorEnergyGapLookupTable(
        rows=[[5700, 5.4606], [5760, 5.5], [6000, 5.681], [6500, 6.045]]
    )
    result = UndulatorEnergyGapLookupTable.from_contents(input)
    assert result == expected
    assert result.get_column_names() == ["energy_eV", "gap_mm"]
