from pydantic import field_validator

from daq_config_server.models.base_model import ConfigModel


class PositionsToTimes(ConfigModel):
    positions_and_times: dict[float, float]

    @field_validator("positions_and_times", mode="after")
    @classmethod
    def _normalise_to_fractions(
        cls, positions_and_rel_times: dict[float, float]
    ) -> dict[float, float]:
        """This allows the time values inside the config file to have arbitary units.
        Once parsed, they will all be as a fraction out of 1, so you can do
        positions_and_rel_times[position] * total_time to get the time for that
        position.
        """
        weighting = 1 / sum(positions_and_rel_times.values())
        return {
            position: rel_time * weighting
            for position, rel_time in positions_and_rel_times.items()
        }
