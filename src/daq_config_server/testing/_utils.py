from unittest.mock import MagicMock

from httpx import Response
from requests import RequestException

from daq_config_server.app import ValidAcceptHeaders


def make_test_response(
    content: str,
    status_code: int = 200,
    raise_exc: type[RequestException] | None = None,
    json_value: str | None = None,
    content_type: ValidAcceptHeaders = ValidAcceptHeaders.PLAIN_TEXT,
):
    r = Response(
        json=json_value,
        status_code=status_code,
        headers={"content-type": content_type},
        content=content,
    )
    r.raise_for_status = MagicMock()

    if raise_exc:
        r.raise_for_status.side_effect = raise_exc
    else:
        r.raise_for_status.return_value = None
    return r
