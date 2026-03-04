import os
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from starlette import status

from daq_config_server.converters._convert import get_converted_file_contents
from daq_config_server.core._whitelist import get_whitelist


def path_is_whitelisted(file_path: Path) -> bool:
    whitelist = get_whitelist()
    return file_path in whitelist.whitelist_files or any(
        file_path.is_relative_to(dir) for dir in whitelist.whitelist_dirs
    )


router = APIRouter()


class ValidAcceptHeaders(StrEnum):
    JSON = "application/json"
    PLAIN_TEXT = "text/plain"
    RAW_BYTES = "application/octet-stream"


@dataclass(frozen=True)
class ENDPOINTS:
    CONFIG = "/config"
    HEALTH = "/healthz"


@router.get(ENDPOINTS.CONFIG + "/{file_path:path}")
def get_configuration(file_path: Path, request: Request):
    if not file_path.is_absolute():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Requested filepath {file_path} must be an absolute path",
        )

    if not path_is_whitelisted(file_path):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{file_path} is not a whitelisted file.",
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
                content = get_converted_file_contents(file_path)
                return JSONResponse(content=content)

            case ValidAcceptHeaders.PLAIN_TEXT:
                with file_path.open("r", encoding="utf-8") as f:
                    return Response(f.read(), media_type=accept)

            case _:
                with file_path.open("rb") as f:
                    return Response(
                        f.read(),
                        media_type=ValidAcceptHeaders.RAW_BYTES,
                    )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                f"Failed to convert {file_name} to {accept}. "
                "Try requesting this file as a different type."
            ),
        ) from e


@router.get("/healthz")
def health_check():
    return Response()
