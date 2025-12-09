import json

import pytest
from tests.constants import TestDataPaths

from daq_config_server.converters.beamline_parameters import (
    beamline_parameters_to_dict,
)


def test_beamline_parameters_to_dict_gives_expected_result():
    with open(TestDataPaths.TEST_BEAMLINE_PARAMETERS_PATH) as f:
        contents = f.read()
    with open(TestDataPaths.EXPECTED_BEAMLINE_PARAMETERS_JSON_PATH) as f:
        expected = json.load(f)
    result = beamline_parameters_to_dict(contents)
    assert result == expected


def test_bad_beamline_parameters_with_non_keyword_string_value_causes_error():
    with open(TestDataPaths.TEST_BAD_BEAMLINE_PARAMETERS_PATH) as f:
        contents = f.read()
    with pytest.raises(ValueError, match="malformed node or string"):
        beamline_parameters_to_dict(contents)


def test_beam_line_parameters_with_repeated_key_causes_error():
    input = "thing = 1\nthing = 2"
    with pytest.raises(ValueError, match="Repeated key in parameters: thing"):
        beamline_parameters_to_dict(input)
