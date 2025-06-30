from pathlib import Path

TEST_DATA_DIR_PATH = Path(f"{Path(__file__).parent}/test_data")

TEST_BEAMLINE_PARAMETERS_PATH = TEST_DATA_DIR_PATH.joinpath("beamline_parameters.txt")

TEST_BAD_JSON_PATH = TEST_DATA_DIR_PATH.joinpath("test_bad_json")

TEST_GOOD_JSON_PATH = TEST_DATA_DIR_PATH.joinpath("test_good_json.json")

TEST_FILE_NOT_ON_WHITELIST_PATH = TEST_DATA_DIR_PATH.joinpath(
    "test_file_not_on_whitelist.json"
)

TEST_FILE_IN_GOOD_DIR = TEST_DATA_DIR_PATH.joinpath("good_dir/test_file")

TEST_FILE_IN_BAD_DIR = TEST_DATA_DIR_PATH.joinpath("bad_dir/test_file")

TEST_INVALID_FILE_PATH = TEST_DATA_DIR_PATH.joinpath("invalid_file")

TEST_CONFIG_PATH = TEST_DATA_DIR_PATH.joinpath("test_config.yaml")

TEST_WHITELIST_RESPONSE = f"""\
whitelist_files:
  - {TEST_GOOD_JSON_PATH}
  - {TEST_BAD_JSON_PATH}
  - {TEST_BEAMLINE_PARAMETERS_PATH}
  - {TEST_INVALID_FILE_PATH}

whitelist_dirs:
  - {TEST_DATA_DIR_PATH.joinpath("good_dir")}
"""
