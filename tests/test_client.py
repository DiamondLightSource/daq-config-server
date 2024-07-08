import pytest
import requests

from daq_config_server.client import ConfigServer

SERVER_ADDRESS = "https://daq-config.diamond.ac.uk/api"


@pytest.fixture
def server():
    return ConfigServer(SERVER_ADDRESS)


@pytest.mark.uses_live_server
class TestConfigServerClient:
    def test_fetch_one_flag_from_server(self, server: ConfigServer):
        assert isinstance(server.get_feature_flag("use_panda_for_gridscan"), bool)

    def test_fetch_all_flags_from_server(self, server: ConfigServer):
        assert isinstance(flags := server.get_feature_flag_list(), list)
        assert all(isinstance(server.get_feature_flag(flag), bool) for flag in flags)

    @pytest.mark.skip(reason="ONLY RUN THIS MANUALLY")
    def test_fetch_and_set_flags(self, server: ConfigServer):
        """ONLY RUN THIS IF YOU ARE SURE NOTHING IS RUNNING USING THE SERVICE!!!"""
        flag = "use_panda_for_gridscan"
        assert isinstance(initial_value := server.get_feature_flag(flag), bool)
        r = requests.put(
            SERVER_ADDRESS
            + f"/featureflag/{flag}?value={str(not initial_value).lower()}"
        )
        assert r.json()["success"] is True
        assert server.get_feature_flag(flag) is not initial_value
        r = requests.put(
            SERVER_ADDRESS + f"/featureflag/{flag}?value={str(initial_value).lower()}"
        )
        assert r.json()["success"] is True
        assert server.get_feature_flag(flag) is initial_value
