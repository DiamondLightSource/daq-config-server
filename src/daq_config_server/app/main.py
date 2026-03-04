import uvicorn

from daq_config_server.app.config import load_config
from daq_config_server.app.log import set_up_logging


def main():
    config = load_config()

    set_up_logging(config.logging)

    uvicorn.run(
        "daq_config_server.app.api:app",
        host="0.0.0.0",
        port=8555,
        workers=config.uvicorn.workers,
    )
