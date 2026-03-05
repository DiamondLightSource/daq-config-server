from daq_config_server.models.lookup_tables._conveters import parse_generic_lut
from daq_config_server.models.lookup_tables._models import GenericLookupTable


def parse_i09_hu_undulator_energy_gap_lut(contents: str) -> GenericLookupTable:
    return parse_generic_lut(
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
