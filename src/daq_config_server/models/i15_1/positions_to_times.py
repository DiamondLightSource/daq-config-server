from pydantic import field_validator

from daq_config_server.models.base_model import ConfigModel
from daq_config_server.models.utils import parse_lut_rows


class AnglesToTimes(ConfigModel):
    tth_angle_to_collection_time: dict[float, float]

    @field_validator("tth_angle_to_collection_time", mode="after")
    @classmethod
    def _normalise_to_fractions(
        cls, angles_and_rel_times: dict[float, float]
    ) -> dict[float, float]:
        """This allows the time values inside the config file to have arbitary units.
        Once parsed, they will all be as a fraction out of 1, so you can do
        positions_and_rel_times[position] * total_time to get the time for that
        position.
        """
        weighting = 1 / sum(angles_and_rel_times.values())
        return {
            position: rel_time * weighting
            for position, rel_time in angles_and_rel_times.items()
        }

    @classmethod
    def from_lut(cls, contents: str):
        rows = parse_lut_rows(contents, types=[float, float])
        return cls(tth_angle_to_collection_time={row[0]: row[1] for row in rows})
