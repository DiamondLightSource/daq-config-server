from pathlib import Path
from unittest.mock import patch

import pytest
from pytest import FixtureRequest

from daq_config_server.testing._utils import make_test_response
from daq_config_server.whitelist import get_whitelist
from tests.constants import TEST_WHITELIST_RESPONSE

WHITELIST_PATH = Path(__file__).resolve().parents[2] / "whitelist.yaml"


@pytest.fixture(autouse=True)
def test_friendly_whitelist(request: FixtureRequest):
    # Don't launch threads unless we really need to since it slows down testing

    with patch("daq_config_server.whitelist.requests.get") as mock_request:
        if "test_whitelist.py" in str(request.path):
            with open(WHITELIST_PATH) as f:
                whitelist_contents = f.read()
            mock_request.return_value = make_test_response(content=whitelist_contents)
        else:
            mock_request.return_value = make_test_response(
                content=TEST_WHITELIST_RESPONSE
            )

        if request.node.get_closest_marker("use_threading"):  # type: ignore
            with patch("daq_config_server.whitelist.WHITELIST_REFRESH_RATE_S", new=0):
                yield
                get_whitelist().stop()
        else:
            with (
                patch("daq_config_server.whitelist.Thread"),
                patch("daq_config_server.whitelist.WhitelistFetcher.stop"),
            ):
                yield

    get_whitelist.cache_clear()
