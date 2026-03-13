from typing import Literal, Self, get_args

from daq_config_server.models.lookup_tables.generic_lut_models import (
    LookupTableBase,
)
from daq_config_server.models.utils import parse_lut_rows

DETECTOR_XY_COLUMN_NAMES = Literal[
    "detector_distance_mm", "beam_centre_x_mm", "beam_centre_y_mm"
]


class DetectorXYLookupTable(LookupTableBase[DETECTOR_XY_COLUMN_NAMES]):
    def get_column_names(self) -> list[DETECTOR_XY_COLUMN_NAMES]:
        return list(get_args(DETECTOR_XY_COLUMN_NAMES))

    @classmethod
    def from_contents(cls, contents: str) -> Self:
        rows = parse_lut_rows(contents, [float, float, float])
        return cls(rows=rows)


BEAMLINE_PITCH_COLUMN_NAMES = Literal["bragg_angle_deg", "pitch_mrad"]


class BeamlinePitchLookupTable(LookupTableBase[BEAMLINE_PITCH_COLUMN_NAMES]):
    def get_column_names(self) -> list[BEAMLINE_PITCH_COLUMN_NAMES]:
        return list(get_args(BEAMLINE_PITCH_COLUMN_NAMES))

    @classmethod
    def from_contents(cls, contents: str) -> Self:
        rows = parse_lut_rows(contents, [float, float])
        return cls(rows=rows)


BEAMLINE_ROLL_COLUMN_NAMES = Literal["bragg_angle_deg", "roll_mrad"]


class BeamlineRollLookupTable(LookupTableBase[BEAMLINE_ROLL_COLUMN_NAMES]):
    def get_column_names(self) -> list[BEAMLINE_ROLL_COLUMN_NAMES]:
        return list(get_args(BEAMLINE_ROLL_COLUMN_NAMES))

    @classmethod
    def from_contents(cls, contents: str) -> Self:
        rows = parse_lut_rows(contents, [float, float])
        return cls(rows=rows)
