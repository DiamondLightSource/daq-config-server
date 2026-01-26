import csv
import io
from collections.abc import Generator
from typing import Any

import numpy as np

from ._models import (
    EnergyCoverage,
    EnergyCoverageEntry,
    InsertionDeviceLookupTable,
    InsertionDeviceLookupTableColumnConfig,
    Pol,
    Source,
)


def read_file_and_skip(file: str, skip_line_start_with: str = "#") -> Generator[str]:
    """Yield non-comment lines from the CSV content string."""
    for line in io.StringIO(file):
        if line.startswith(skip_line_start_with):
            continue
        else:
            yield line


def convert_csv_to_lookup(
    file_contents: str,
    lut_config: InsertionDeviceLookupTableColumnConfig,
    skip_line_start_with: str = "#",
) -> InsertionDeviceLookupTable:
    """
    Convert CSV content into the Apple2 lookup-table dictionary.

    Parameters:
    -----------
    file_contents:
        The CSV file contents as string.
    lut_config:
        The configuration that how to process the file_contents into a LookupTable.
    skip_line_start_with
        Lines beginning with this prefix are skipped (default "#").

    Returns:
    -----------
    LookupTable
    """
    temp_mode_entries: dict[Pol, list[EnergyCoverageEntry]] = {}

    def process_row(row: dict[str, Any]) -> None:
        """Process a single row from the CSV file and update the temporary entry
        list."""
        raw_mode_value = str(row[lut_config.mode]).lower()
        mode_value = Pol(
            lut_config.mode_name_convert.get(raw_mode_value, raw_mode_value)
        )

        coefficients = np.poly1d([float(row[coef]) for coef in lut_config.poly_deg])

        energy_entry = EnergyCoverageEntry(
            min_energy=float(row[lut_config.min_energy]),
            max_energy=float(row[lut_config.max_energy]),
            poly=coefficients,
        )

        if mode_value not in temp_mode_entries:
            temp_mode_entries[mode_value] = []

        temp_mode_entries[mode_value].append(energy_entry)

    reader = csv.DictReader(read_file_and_skip(file_contents, skip_line_start_with))

    for row in reader:
        source = lut_config.source
        # If there are multiple source only convert requested.
        if source is None or row[source.column] == source.value:
            process_row(row=row)
    # Check if our LookupTable is empty after processing, raise error if it is.
    if not temp_mode_entries:
        raise RuntimeError(
            "LookupTable content is empty, failed to convert the file contents to "
            "a LookupTable!"
        )

    final_lut_root: dict[Pol, EnergyCoverage] = {}
    for pol, entries in temp_mode_entries.items():
        final_lut_root[pol] = EnergyCoverage.model_validate({"energy_entries": entries})

    return InsertionDeviceLookupTable(root=final_lut_root)


"""Implementations for each beamline"""


def parse_i10_gap_idd_lut(contents: str) -> InsertionDeviceLookupTable:
    source = Source(column="Source", value="idd")
    lut_config = InsertionDeviceLookupTableColumnConfig(source=source)
    return convert_csv_to_lookup(contents, lut_config)


def parse_i10_gap_idu_lut(contents: str) -> InsertionDeviceLookupTable:
    source = Source(column="Source", value="idu")
    lut_config = InsertionDeviceLookupTableColumnConfig(source=source)
    return convert_csv_to_lookup(contents, lut_config)


def parse_i10_phase_idd_lut(contents: str) -> InsertionDeviceLookupTable:
    source = Source(column="Source", value="idd")
    lut_config = InsertionDeviceLookupTableColumnConfig(source=source)
    return convert_csv_to_lookup(contents, lut_config)


def parse_i10_phase_idu_lut(contents: str) -> InsertionDeviceLookupTable:
    source = Source(column="Source", value="idu")
    lut_config = InsertionDeviceLookupTableColumnConfig(source=source)
    return convert_csv_to_lookup(contents, lut_config)


def parse_i09_2_gap_id_lut(contents: str) -> InsertionDeviceLookupTable:
    lut_config = InsertionDeviceLookupTableColumnConfig(
        poly_deg=[
            "9th-order",
            "8th-order",
            "7th-order",
            "6th-order",
            "5th-order",
            "4th-order",
            "3rd-order",
            "2nd-order",
            "1st-order",
            "0th-order",
        ]
    )
    return convert_csv_to_lookup(contents, lut_config)


def parse_i09_2_phase_id_lut(contents: str) -> InsertionDeviceLookupTable:
    lut_config = InsertionDeviceLookupTableColumnConfig(poly_deg=["0th-order"])
    return convert_csv_to_lookup(contents, lut_config)


def parse_i21_gap_id_lut(contents: str) -> InsertionDeviceLookupTable:
    lut_config = InsertionDeviceLookupTableColumnConfig(grating="Grating")
    return convert_csv_to_lookup(contents, lut_config)


def parse_i21_phase_id_lut(contents: str) -> InsertionDeviceLookupTable:
    lut_config = InsertionDeviceLookupTableColumnConfig(
        grating="Grating", poly_deg=["b"]
    )
    return convert_csv_to_lookup(contents, lut_config)
