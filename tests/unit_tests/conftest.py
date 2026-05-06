from pathlib import Path
from unittest.mock import patch

import pytest
from _pytest.tmpdir import TempPathFactory
from pytest import FixtureRequest

from daq_config_server.app._config import WhitelistConfig
from daq_config_server.app._whitelist import (
    init_whitelist,
)
from tests.constants import TEST_WHITELIST_RESPONSE

DEFAULT_WHITELIST = (
    Path(__file__).resolve().parents[2] / "helm/daq-config-server/whitelist.yaml"
)


@pytest.fixture(scope="session")
def tmp_whitelist(tmp_path_factory: TempPathFactory) -> Path:
    tmp_whitelist = tmp_path_factory.mktemp("yaml") / "test_whitelist.yaml"
    with tmp_whitelist.open("w") as whitelist_stream:
        whitelist_stream.write(TEST_WHITELIST_RESPONSE)
    return tmp_whitelist


@pytest.fixture(autouse=True)
def patch_whitelist_fetch(tmp_whitelist: Path, request: FixtureRequest):
    test_module_path = request.path
    if "test_whitelist.py" not in str(test_module_path):
        with (
            patch("daq_config_server.app._whitelist.Thread"),
            patch("daq_config_server.app._whitelist.FilesystemWhitelist.stop"),
        ):
            init_whitelist(WhitelistConfig(config_file=str(tmp_whitelist)))
            yield
    else:
        yield
