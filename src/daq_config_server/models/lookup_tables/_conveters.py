from daq_config_server.converters._converter_utils import parse_lut_rows
from daq_config_server.models.lookup_tables._models import GenericLookupTable

IGNORE_LINES_STARTING_WITH = ("Units", "ScannableUnits", "ScannableNames")


def parse_generic_lut(
    contents: str, *params: tuple[str, type | None]
) -> GenericLookupTable:
    """Converts a lookup table to a pydantic model, containing the names of each column
    and the rows as a 2D list.

    Any args after the contents provide the column names and optionally, python types
    for values in a column to be converted to. e.g: ("energy_EV", float),
    ("pixels", int). If a type is provided, the values in that column will be converted
    to that type. Otherwise, the type will be inferred. Units should be included in the
    column name.
    """
    column_names = [param[0] for param in params]
    types = [param[1] for param in params]
    rows = parse_lut_rows(contents, types)
    return GenericLookupTable(column_names=column_names, rows=rows)
