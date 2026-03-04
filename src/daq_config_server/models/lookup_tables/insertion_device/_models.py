from typing import Literal, get_args

from daq_config_server.models.lookup_tables._models import LookupTableBase

UNDULATOR_ENERGY_GAP_COLUMN_NAMES = Literal["energy_eV", "gap_mm"]


class UndulatorEnergyGapLookupTable(LookupTableBase[UNDULATOR_ENERGY_GAP_COLUMN_NAMES]):
    def get_column_names(self) -> list[UNDULATOR_ENERGY_GAP_COLUMN_NAMES]:
        return list(get_args(UNDULATOR_ENERGY_GAP_COLUMN_NAMES))
