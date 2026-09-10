from typing import Literal, Self, get_args

from daq_config_server.models.lookup_tables.generic_lut_models import (
    GenericLookupTable,
    LookupTableBase,
)
from daq_config_server.models.utils import get_units_from_lut, parse_lut_rows

UNDULATOR_ENERGY_GAP_COLUMN_NAMES = Literal["energy_eV", "gap_mm"]
EXPECTED_UNITS = ["eV", "mm"]


def _check_energy_units_and_convert_row(
    rows: list[list[float]],
    units_from_table: str,
    default_energy_unit: str = EXPECTED_UNITS[0],
) -> list[list[float]]:
    if units_from_table.lower() == default_energy_unit.lower():
        return rows
    elif units_from_table.lower() == "kev":
        return [[row[0] * 1000, row[1]] for row in rows]
    else:
        raise ValueError(
            f"""No conversion implemented for units: {units_from_table}.
            Energy in table should be in eV or KeV."""
        )


class UndulatorEnergyGapLookupTable(LookupTableBase[UNDULATOR_ENERGY_GAP_COLUMN_NAMES]):
    def get_column_names(self) -> list[UNDULATOR_ENERGY_GAP_COLUMN_NAMES]:
        return list(get_args(UNDULATOR_ENERGY_GAP_COLUMN_NAMES))

    @classmethod
    def from_contents(cls, contents: str) -> Self:
        rows = parse_lut_rows(contents, [float, float])
        rows = _check_energy_units_and_convert_row(
            rows, get_units_from_lut(contents, EXPECTED_UNITS)[0]
        )
        return cls(rows=rows)


def parse_i09_hu_undulator_energy_gap_lut(contents: str) -> GenericLookupTable:
    return GenericLookupTable.from_contents(
        contents,
        ("order", int),
        ("ring_energy_gev", float),
        ("magnetic_field_t", float),
        ("energy_min_ev", float),
        ("energy_max_ev", float),
        ("gap_min_mm", float),
        ("gap_max_mm", float),
        ("gap_offset_mm", float),
    )
