from dataclasses import dataclass
from pathlib import Path

TEST_I15_1_DATA_DIR_PATH = Path(
    f"{Path(__file__).parent.parent.parent.parent}/test_data/i15_1"
)


@dataclass
class TestI151DataPaths:
    __test__ = False  # Stops pytest complaining about the class name
    XPDF_LOCAL_PARAMETERS = TEST_I15_1_DATA_DIR_PATH.joinpath(
        "test_xpdfLocalParameters.xml"
    )
    XPDF_CRYSTAL_LUT = TEST_I15_1_DATA_DIR_PATH.joinpath(
        "test_i15-1_xpdf_crystal_lut.txt"
    )
    POSITIONS_TIMES_LUT = TEST_I15_1_DATA_DIR_PATH.joinpath(
        "test_tth_angle_to_collection_time.txt"
    )
    STANDARDS_PUCK = TEST_I15_1_DATA_DIR_PATH.joinpath("test_standards_puck.json")
    TEMPERATURE_CALIBRATION = TEST_I15_1_DATA_DIR_PATH.joinpath(
        "test_temperature_calibration.txt"
    )
