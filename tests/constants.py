from dataclasses import dataclass
from pathlib import Path

TEST_DATA_DIR_PATH = Path(f"{Path(__file__).parent}/test_data")


@dataclass
class TestDataPaths:
    __test__ = False  # Stops pytest complaining about the class name

    TEST_BEAMLINE_PARAMETERS_PATH = TEST_DATA_DIR_PATH.joinpath(
        "beamline_parameters.txt"
    )

    TEST_BAD_JSON_PATH = TEST_DATA_DIR_PATH.joinpath("test_bad_json")

    TEST_GOOD_JSON_PATH = TEST_DATA_DIR_PATH.joinpath("test_good_json.json")

    TEST_FILE_NOT_ON_WHITELIST_PATH = TEST_DATA_DIR_PATH.joinpath(
        "test_file_not_on_whitelist.json"
    )

    TEST_FILE_IN_GOOD_DIR = TEST_DATA_DIR_PATH.joinpath("good_dir/test_file")

    TEST_FILE_IN_BAD_DIR = TEST_DATA_DIR_PATH.joinpath("bad_dir/test_file")

    TEST_INVALID_FILE_PATH = TEST_DATA_DIR_PATH.joinpath("invalid_file")


# These are the file locations accessible from the server running in a container
@dataclass
class ServerFilePaths:
    BEAMLINE_PARAMETERS = Path("/tests/test_data/beamline_parameters.txt")
    GOOD_JSON_FILE = Path("/tests/test_data/test_good_json.json")
    BAD_JSON_FILE = Path("/tests/test_data/test_bad_json")
    FILE_IN_GOOD_DIR = Path("/tests/test_data/test_bad_json")


TEST_CONFIG_PATH = TEST_DATA_DIR_PATH.joinpath("test_config.yaml")

TEST_WHITELIST_RESPONSE = f"""\
whitelist_files:
  - {TestDataPaths.TEST_GOOD_JSON_PATH}
  - {TestDataPaths.TEST_BAD_JSON_PATH}
  - {TestDataPaths.TEST_BEAMLINE_PARAMETERS_PATH}
  - {TestDataPaths.TEST_INVALID_FILE_PATH}

whitelist_dirs:
  - {TEST_DATA_DIR_PATH.joinpath("good_dir")}
"""
