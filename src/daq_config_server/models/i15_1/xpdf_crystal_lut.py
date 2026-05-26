from typing import Literal, Self, get_args

from daq_config_server.models.lookup_tables.generic_lut_models import LookupTableBase
from daq_config_server.models.utils import parse_lut_rows

XPDF_CRYSTAL_COLUMN_NAMES = Literal["y_mm", "energy_keV"]


class XpdfCrystalLookupTable(LookupTableBase[XPDF_CRYSTAL_COLUMN_NAMES]):
    # Unlike most other config in the config server, this is never read by GDA.
    # For this reason it's a good candidate for storing in a database such as
    # redis, instead of on the file system.
    # See https://github.com/DiamondLightSource/daq-config-server/issues/184
    def get_column_names(self) -> list[XPDF_CRYSTAL_COLUMN_NAMES]:
        return list(get_args(XPDF_CRYSTAL_COLUMN_NAMES))

    @classmethod
    def from_contents(cls, contents: str) -> Self:
        rows = parse_lut_rows(contents, [float, float])
        return cls(rows=rows)

    def get_energy(self, y: float) -> float:
        return self.get_value("y_mm", y, "energy_keV", value_must_exist=False)
