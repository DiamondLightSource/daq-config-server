from pydantic import BaseModel, field_validator

from daq_config_server.models.base_model import ConfigModel
from daq_config_server.models.utils import parse_lut_rows


class SpecificationPerPosition(BaseModel):
    exposure_time: float
    transmission: float


class CollectionSpecification(ConfigModel):
    tth_angle_to_specification: dict[float, SpecificationPerPosition]

    @field_validator("tth_angle_to_specification", mode="after")
    @classmethod
    def _normalise_to_fractions(
        cls,
        angles_spec: dict[float, SpecificationPerPosition],
    ) -> dict[float, SpecificationPerPosition]:
        """This allows the time values inside the config file to have arbitrary units.
        Once parsed, they will all be as a fraction out of 1, so you can do
        positions_and_rel_times[position] * total_time to get the time for that
        position.
        """
        weighting = 1 / sum([spec.exposure_time for spec in angles_spec.values()])
        for spec in angles_spec.values():
            spec.exposure_time *= weighting

        return angles_spec

    @classmethod
    def from_lut(cls, contents: str):
        rows = parse_lut_rows(contents, types=[float, float, float])
        return cls(
            tth_angle_to_specification={
                row[0]: SpecificationPerPosition(
                    exposure_time=row[1], transmission=row[2]
                )
                for row in rows
            }
        )
