from unittest.mock import MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from config_service.app import app


@pytest.fixture
def mock_app():
    return TestClient(app)


@patch("config_service.app.valkey")
def test_get_beamlineparam(mock_valkey: MagicMock, mock_app):
    test_param_list = ["param_1", "param_2", "param_3"]
    mock_valkey.smembers.return_value = test_param_list
    response = mock_app.get("featurelist")
    assert response.status_code == status.HTTP_200_OK
