import pytest

from daq_config_server.whitelist import get_whitelist


@pytest.fixture(autouse=True)
def cleanup_whitelist():
    # Make sure we stop the background thread cleanly after each unit test
    yield
    get_whitelist().stop()
