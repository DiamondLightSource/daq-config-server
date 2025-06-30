import json
import logging
import os
from collections.abc import Awaitable, Callable
from enum import StrEnum
from pathlib import Path

import uvicorn
import yaml
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from starlette import status

from daq_config_server.config import Config
from daq_config_server.constants import (
    ENDPOINTS,
)
from daq_config_server.log import set_up_logging
from daq_config_server.whitelist import get_whitelist

# See https://github.com/DiamondLightSource/daq-config-server/issues/105
# to make this path configurable
CONFIG_PATH = "/etc/config/config.yaml"

LOGGER = logging.getLogger(__name__)


async def log_request_details(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    LOGGER.debug(
        f"method: {request.method} url: {request.url} body: {await request.body()}",
    )
    response = await call_next(request)
    return response


app = FastAPI(
    title="DAQ config server",
    description="""For reading files stored on /dls_sw from another container""",
)
origins = ["*"]
app.middleware("http")(log_request_details)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

__all__ = ["main"]


class ValidAcceptHeaders(StrEnum):
    JSON = "application/json"
    PLAIN_TEXT = "text/plain"
    RAW_BYTES = "application/octet-stream"


def path_is_whitelisted(file_path: Path) -> bool:
    whitelist = get_whitelist()
    return file_path in whitelist.whitelist_files or any(
        file_path.is_relative_to(dir) for dir in whitelist.whitelist_dirs
    )


@app.get(
    ENDPOINTS.CONFIG + "/{file_path:path}",
    responses={
        200: {
            "description": "Returns JSON, plain text, or binary file.",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "additionalProperties": True,
                        "example": {
                            "key": "value",
                            "list": [1, 2, 3],
                            "nested": {"a": 1},
                        },
                    }
                },
                "text/plain": {
                    "schema": {
                        "type": "string",
                        "example": "This is a plain text response",
                    }
                },
                "application/octet-stream": {
                    "schema": {"type": "string", "format": "binary"},
                },
            },
        },
    },
)
def get_configuration(
    file_path: Path,
    request: Request,
):
    """
    Read a file and return its contents in a format specified by the accept header.

    Check the file against the whitelist on the current main branch on GitHub.
    """

    if not file_path.is_absolute():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(f"Requested filepath {file_path} must be an absolute path"),
        )

    if not path_is_whitelisted(file_path):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{file_path} is not a whitelisted file. Please make sure it \
            exists in https://raw.githubusercontent.com/DiamondLightSource/\
            daq-config-server/refs/heads/main/whitelist.yaml",
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_path} cannot be found",
        )

    file_name = os.path.basename(file_path)
    accept = request.headers.get("accept", ValidAcceptHeaders.PLAIN_TEXT)

    try:
        match accept:
            case ValidAcceptHeaders.JSON:
                with file_path.open("r", encoding="utf-8") as f:
                    content = json.loads(f.read())
                return JSONResponse(
                    content=content,
                )
            case ValidAcceptHeaders.PLAIN_TEXT:
                with file_path.open("r", encoding="utf-8") as f:
                    content = f.read()
                return Response(content=content, media_type=accept)
            case _:
                with file_path.open("rb") as f:
                    content = f.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Failed to convert {file_name} to {accept}. "
                "Try requesting this file as a different type."
            ),
        ) from e

    return Response(content=content, media_type=ValidAcceptHeaders.RAW_BYTES)


@app.get("/healthz")
def health_check():
    """
    Kubernetes health check
    """
    return Response()


def main():
    # Set up logging with defaults, or using config.yaml if it exists
    if os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            data = yaml.safe_load(f)
            config = Config(**data)
    else:
        config = Config()

    set_up_logging(config.logging_config)

    uvicorn.run(app="daq_config_server.app:app", host="0.0.0.0", port=8555)
