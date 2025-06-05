from unittest.mock import MagicMock, patch

import pytest
from pytest import FixtureRequest

from daq_config_server.whitelist import get_whitelist
from tests.constants import (
    WHITELIST_PATH,
)


@pytest.fixture(autouse=True)
def test_friendly_whitelist(request: FixtureRequest):
    # Don't launch threads unless we really need to since it slows down testing

    if request.node.get_closest_marker("use_threading"):  # type: ignore
        with patch("daq_config_server.whitelist.WHITELIST_REFRESH_RATE_S", new=0):
            yield
            get_whitelist().stop()

    else:

        def fake_whitelist_get():
            response = MagicMock()
            response.text = WHITELIST_PATH.read_text()
            return response

        with (
            patch("daq_config_server.whitelist.Thread"),
            patch("daq_config_server.whitelist.WhitelistFetcher.stop"),
            patch("daq_config_server.whitelist.requests.get") as fake_get,
        ):
            fake_get.return_value = fake_whitelist_get()
            yield

    from daq_config_server import whitelist

    whitelist._whitelist_instance = None
