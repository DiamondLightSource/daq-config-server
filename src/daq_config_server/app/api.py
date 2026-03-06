import logging
from collections.abc import Awaitable, Callable

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from daq_config_server.app._config import load_config
from daq_config_server.app._log import set_up_logging
from daq_config_server.app._routes import router

LOGGER = logging.getLogger(__name__)


async def log_request_details(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    LOGGER.debug(
        f"method: {request.method} url: {request.url} body: {await request.body()}"
    )
    return await call_next(request)


app = FastAPI(
    title="DAQ config server",
    description="For reading files stored on /dls_sw from another container",
)

app.middleware("http")(log_request_details)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


def main():
    config = load_config()

    set_up_logging(config.logging)

    uvicorn.run(
        "daq_config_server.app.api:app",
        host="0.0.0.0",
        port=8555,
        workers=config.uvicorn.workers,
    )
