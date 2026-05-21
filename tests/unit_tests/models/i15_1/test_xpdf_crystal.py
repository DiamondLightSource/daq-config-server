import pytest
from tests.constants import TestDataPaths

from daq_config_server.models.i15_1.xpdf_crystal_lut import XpdfCrystalLookupTable


def test_xpdf_crystal_lut_is_read_correctly():
    with open(TestDataPaths.TEST_I15_1_XPDF_CRYSTAL_LUT) as f:
        contents = f.read()
    expected = XpdfCrystalLookupTable(
        rows=[[1.455, 40.05], [-48.845, 65.4], [50.6, 76.69]]
    )
    result = XpdfCrystalLookupTable.from_contents(contents)
    assert result == expected


@pytest.mark.parametrize(
    "y, expected_energy",
    [
        (1.455, 40.05),
        (0, 40.05),
        (-48.845, 65.4),
        (-50.999, 65.4),
        (50.6, 76.69),
        (51.7, 76.69),
    ],
)
def test_get_energy_returns_expected_energy_based_on_y(
    y: float, expected_energy: float
):
    with open(TestDataPaths.TEST_I15_1_XPDF_CRYSTAL_LUT) as f:
        contents = f.read()

    lut = XpdfCrystalLookupTable.from_contents(contents)
    assert lut.get_energy(y) == expected_energy
