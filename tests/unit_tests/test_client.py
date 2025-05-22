from unittest.mock import MagicMock, patch

from fastapi import status
from httpx import Response

from daq_config_server.app import ValidAcceptHeaders
from daq_config_server.client import ConfigServer, RequestedResponseFormats
from daq_config_server.constants import ENDPOINTS


@patch("daq_config_server.client.requests.get")
def test_get_file_contents_default_header(mock_request: MagicMock):
    content_type = ValidAcceptHeaders.PLAIN_TEXT
    mock_request.return_value = Response(
        status_code=status.HTTP_200_OK,
        content="test",
        headers={
            "content-type": content_type,
        },
    )
    file_path = "test"
    url = "url"
    server = ConfigServer(url)
    assert server.get_file_contents(file_path) == "test"
    mock_request.assert_called_once_with(
        url + ENDPOINTS.CONFIG + "/" + file_path,
        headers={"Accept": RequestedResponseFormats.DECODED_STRING},
    )


@patch("daq_config_server.client.requests.get")
def test_get_file_contents_warns_and_gives_bytes_on_invalid_json(
    mock_request: MagicMock,
):
    content_type = ValidAcceptHeaders.JSON
    bad_json = "bad_dict}"
    mock_request.return_value = Response(
        status_code=status.HTTP_200_OK,
        json="test",
        headers={
            "content-type": content_type,
        },
        content=bad_json,
    )
    file_path = "test"
    url = "url"
    server = ConfigServer(url)
    server._log.warning = MagicMock()
    assert (
        server.get_file_contents(
            file_path, requested_response_format=RequestedResponseFormats.DICT
        )
        == bad_json.encode()
    )
    assert (
        f"Failed trying to convert to content-type {content_type} due to "
        in server._log.warning.call_args[0][0]
    )


@patch("daq_config_server.client.requests.get")
def test_logger_warning_if_content_type_doesnt_match_requested_type(
    mock_request: MagicMock,
):
    headers = {"Accept": RequestedResponseFormats.DICT}
    content_type = ValidAcceptHeaders.PLAIN_TEXT
    text = "text"
    mock_request.return_value = Response(
        status_code=status.HTTP_200_OK,
        headers={
            "content-type": content_type,
        },
        content=text,
    )
    file_path = "test"
    url = "url"
    server = ConfigServer(url)
    server._log.warning = MagicMock()
    server.get_file_contents(
        file_path, requested_response_format=RequestedResponseFormats.DICT
    )

    server._log.warning.assert_called_once_with(
        f"Server failed to parse the file as requested. Requested \
                {headers['Accept']} but response came as content-type {content_type}"
    )
