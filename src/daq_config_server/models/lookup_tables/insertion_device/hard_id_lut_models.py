from typing import Literal, get_args

from daq_config_server.models.lookup_tables.generic_lut_models import (
    GenericLookupTable,
    LookupTableBase,
)

UNDULATOR_ENERGY_GAP_COLUMN_NAMES = Literal["energy_eV", "gap_mm"]


class UndulatorEnergyGapLookupTable(LookupTableBase[UNDULATOR_ENERGY_GAP_COLUMN_NAMES]):
    def get_column_names(self) -> list[UNDULATOR_ENERGY_GAP_COLUMN_NAMES]:
        return list(get_args(UNDULATOR_ENERGY_GAP_COLUMN_NAMES))


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
