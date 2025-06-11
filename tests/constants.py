from pathlib import Path

TEST_DATA_DIR_PATH = Path(f"{Path(__file__).parent}/test_data")

TEST_BEAMLINE_PARAMETERS_PATH = TEST_DATA_DIR_PATH.joinpath("beamline_parameters.txt")

TEST_BAD_JSON_PATH = TEST_DATA_DIR_PATH.joinpath("test_bad_json")

TEST_GOOD_JSON_PATH = TEST_DATA_DIR_PATH.joinpath("test_good_json.json")
