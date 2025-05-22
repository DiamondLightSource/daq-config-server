from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from daq_config_server.constants import ENDPOINTS

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


@app.get(ENDPOINTS.CONFIG + "/{file_path:path}")
def get_configuration(file_path: Path):
    """Read a file and return its contents completely unformatted as a string. After
    https://github.com/DiamondLightSource/daq-config-server/issues/67, this endpoint
    will convert commonly read files to a dictionary format
    """
    if not file_path.is_file():
        raise FileNotFoundError(f"File {file_path} cannot be found")

    with file_path.open("r", encoding="utf-8") as f:
        return f.read()


def main():
    uvicorn.run(app="daq_config_server.app:app", host="0.0.0.0", port=8555)
