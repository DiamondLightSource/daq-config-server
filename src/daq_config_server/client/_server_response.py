from collections.abc import Mapping
from pathlib import Path
from typing import Any, Protocol

import requests
from requests import Response as RealResponse
from requests.exceptions import HTTPError

from daq_config_server.app.constants import ValidAcceptHeaders


class ResponseProtocol(Protocol):
    def json(self) -> Any: ...

    @property
    def headers(self) -> Mapping[str, str]: ...

    @property
    def text(self) -> str: ...

    @property
    def content(self) -> bytes: ...


class ServerResponse(Protocol):
    """Interface for retrieving configuration data from either a real server or a local
    mock implementation.
    """

    url: str

    def get_response(
        self, endpoint: str, accept_header: ValidAcceptHeaders, file_path: Path
    ) -> ResponseProtocol: ...


class RealServerResponse(ServerResponse):
    """Real HTTP implementation of ServerResponse used in production.

    This class communicates with a remote configuration server via HTTP
    requests and retrieves file contents from a deployed service.
    """

    def __init__(self, url: str = "https://daq-config.diamond.ac.uk"):
        self.url = url

    def get_response(
        self, endpoint: str, accept_header: ValidAcceptHeaders, file_path: Path
    ) -> RealResponse:
        """
        Get data from the config server and cache it.

        Args:
            endpoint: API endpoint.
            accept_header: Accept header MIME type
            file_path: absolute path to the file which will be read

        Returns:
            The response data.
        """

        request_url = self.url + endpoint + (f"/{file_path}")
        r = requests.get(request_url, headers={"Accept": accept_header})
        # Intercept http exceptions from server so that the client
        # can include the response `detail` sent by the server
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            try:
                error_detail = r.json().get("detail")
            except ValueError:
                error_detail = None

            if error_detail is None:
                error_detail = "Response raised HTTP error but no details provided"
            raise HTTPError(error_detail) from err

        return r
