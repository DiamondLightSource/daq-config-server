import json
import os
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import uvicorn
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from daq_config_server.constants import ENDPOINTS
from daq_config_server.log import LOGGER

app = FastAPI(
    title="DAQ config server",
    description="""For reading files stored on /dls_sw from another container""",
)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

__all__ = ["main"]


class AcceptedFileTypes(StrEnum):
    JSON = "application/json"
    PLAIN_TEXT = "text/plain"
    RAW_BYTES = "application/octet-stream"


@app.get(ENDPOINTS.CONFIG + "/{file_path:path}")
def get_configuration(
    file_path: Path,
    accept: Annotated[AcceptedFileTypes, Header()] = AcceptedFileTypes.PLAIN_TEXT,
):
    """
    Read a file and return its contents in a format specified by the accept header.
    """
    if not file_path.is_file():
        raise FileNotFoundError(f"File {file_path} cannot be found")

    file_name = os.path.basename(file_path)

    try:
        match accept:
            case AcceptedFileTypes.JSON:
                with file_path.open("r", encoding="utf-8") as f:
                    content = json.loads(f.read())
                return JSONResponse(
                    content=content,
                )
            case AcceptedFileTypes.PLAIN_TEXT:
                with file_path.open("r", encoding="utf-8") as f:
                    content = f.read()
                return Response(content=content, media_type=accept)
    except Exception as e:
        LOGGER.warning(
            f"Failed to convert {file_name} to {accept} and caught \
            exception: {e} \nSending file as raw bytes instead"
        )

    with file_path.open("rb") as f:
        content = f.read()

    return Response(content=content, media_type=AcceptedFileTypes.RAW_BYTES)


def main():
    uvicorn.run(app="daq_config_server.app:app", host="0.0.0.0", port=8555)
