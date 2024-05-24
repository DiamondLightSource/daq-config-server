import json
from http.client import HTTPConnection

from .constants import ENDPOINTS


class ConfigService:
    def __init__(self, address: str, port: int) -> None:
        self.address = address
        self.port = port

    def _get(self, endpoint: str, param: str):
        conn = HTTPConnection(self.address, self.port)
        conn.connect()
        conn.request("GET", f"{endpoint}{param}")
        resp = conn.getresponse()
        assert resp.status == 200, f"Failed to get response: {resp}"
        body = json.loads(resp.read())
        assert param in body, f"Malformed response: {body} does not contain {param}"
        resp.close()
        conn.close()
        return body[param]

    def get_beamline_param(self, param: str) -> str | int | float | bool | None:
        return self._get(ENDPOINTS.BL_PARAM, param)

    def get_feature_flag(self, param: str) -> bool | None:
        return self._get(ENDPOINTS.FEATURE, param)
