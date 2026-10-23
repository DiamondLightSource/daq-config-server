from daq_config_server.models.i15_1.queue_parameters import (
    CentringParameters,
    DataCollectionParameters,
    QueueParameters,
)

from .conftest import TestI151DataPaths


def test_queue_parameters_toml_read_correctly():
    with open(TestI151DataPaths.QUEUE_PARAMETERS) as f:
        contents = f.read()

    expected = QueueParameters(
        do_wait_for_beam=True,
        do_robot_load=True,
        do_centring=True,
        add_auxiliary_scans=True,
        tiled_stale_time_s=604800,
        room_temperature_centring_params=CentringParameters(
            start_z=-20.0, end_z=7.0, step_size_mm=0.1, exposure_time_per_frame_s=0.1
        ),
        blower_centring_params=CentringParameters(
            start_z=-10.0, end_z=5.0, step_size_mm=0.1, exposure_time_per_frame_s=0.1
        ),
        data_collection_params=DataCollectionParameters(exposure_time_per_frame_s=1.0),
    )

    result = QueueParameters.from_toml(contents)

    assert result == expected
