import tomllib

from daq_config_server.models import ConfigModel


class CentringParameters(ConfigModel):
    start_z: float
    end_z: float
    step_size_mm: float
    exposure_time_per_frame_s: float


class DataCollectionParameters(ConfigModel):
    exposure_time_per_frame_s: float


class QueueParameters(ConfigModel):
    do_wait_for_beam: bool
    do_robot_load: bool
    do_centring: bool
    add_auxiliary_scans: bool
    tiled_stale_time_s: int
    room_temperature_centring_params: CentringParameters
    blower_centring_params: CentringParameters
    data_collection_params: DataCollectionParameters

    @classmethod
    def from_toml(cls, contents: str) -> "QueueParameters":
        return cls.model_validate(tomllib.loads(contents))
