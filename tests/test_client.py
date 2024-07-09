import pytest
import requests

from daq_config_server.client import ConfigServer

SERVER_ADDRESS = "http://localhost:8555"  # "https://daq-config.diamond.ac.uk/api"
USE_PANDA_FLAG = "use_panda_for_gridscan"


@pytest.fixture
def server():
    return ConfigServer(SERVER_ADDRESS)


@pytest.mark.uses_live_server
class TestConfigServerClient:
    def test_fetch_one_flag_from_server(self, server: ConfigServer):
        assert isinstance(server.get_feature_flag(USE_PANDA_FLAG), bool)

    def test_fetch_all_flags_from_server(self, server: ConfigServer):
        assert isinstance(flags := server.get_feature_flag_list(), list)
        assert all(isinstance(server.get_feature_flag(flag), bool) for flag in flags)

    def test_best_effort_gets_real_flag(self, server: ConfigServer):
        assert isinstance(current := server.get_feature_flag(USE_PANDA_FLAG), bool)
        assert (
            server.best_effort_get_feature_flag(USE_PANDA_FLAG, not current) is current
        )

    @pytest.mark.skip(reason="ONLY RUN THIS MANUALLY")
    def test_fetch_and_set_flags(self, server: ConfigServer):
        """ONLY RUN THIS IF YOU ARE SURE NOTHING IS RUNNING USING THE SERVICE!!!"""
        flag = USE_PANDA_FLAG
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

    def test_get_some_beamline_params(self, server: ConfigServer):
        params_list = [
            "miniap_x_ROBOT_LOAD",
            "miniap_y_ROBOT_LOAD",
            "miniap_z_ROBOT_LOAD",
        ]
        params = server.get_some_beamline_params(params_list)
        assert all(p in params.keys() for p in params_list)
