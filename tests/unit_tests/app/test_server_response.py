import json

from daq_config_server.app._routes import ValidAcceptHeaders
from daq_config_server.app._server_response import MockResponse


def test_mock_response_using_bytes():
    data = {"x": 1, "y": "test"}
    body = json.dumps(data).encode()
    resp = MockResponse(body=body, content_type=ValidAcceptHeaders.JSON)
    assert resp.json() == data
    assert resp.text == json.dumps(data)
    assert resp.content == body
