import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from config_service.app import app
from config_service.beamline_parameters import GDABeamlineParameters
from config_service.constants import ENDPOINTS

mock_bl_params = GDABeamlineParameters()
mock_bl_params.params = {"p1": 0.234, "p2": 0.345, "p3": 678}


@pytest.fixture
def mock_app():
    return TestClient(app)


async def _assert_get_and_response(
    client: TestClient, endpoint: str, expected_response: Any
):
    response = client.get(endpoint)
    assert response.status_code == status.HTTP_200_OK
    content = json.loads(await response.aread())
    assert content == expected_response


@patch("config_service.app.BEAMLINE_PARAMS", mock_bl_params)
class TestApi:
    async def test_get_all_beamlineparams(self, mock_app):
        await _assert_get_and_response(
            mock_app, ENDPOINTS.BL_PARAM, mock_bl_params.params
        )

    async def test_get_one_beamlineparam(self, mock_app):
        param = "p3"
        await _assert_get_and_response(
            mock_app,
            ENDPOINTS.BL_PARAM + f"/{param}",
            {param: mock_bl_params.params[param]},
        )

    @patch("config_service.app.valkey")
    async def test_get_feature_list(self, mock_valkey: MagicMock, mock_app):
        test_param_list = ["param_1", "param_2", "param_3"]
        mock_valkey.smembers.return_value = test_param_list
        await _assert_get_and_response(
            mock_app,
            ENDPOINTS.FEATURE,
            test_param_list,
        )
