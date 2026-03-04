from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from daq_config_server.app.api import app, log_request_details


@pytest.fixture
def mock_app():
    return TestClient(app)


async def test_log_request_details():
    with patch("daq_config_server.app.api.LOGGER") as logger:
        app = FastAPI()
        app.middleware("http")(log_request_details)

        @app.get("/")
        async def root():  # type: ignore
            return {"message": "Hello World"}

        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        logger.debug.assert_called_once_with(
            "method: GET url: http://testserver/ body: b''"
        )
