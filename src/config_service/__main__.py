from argparse import ArgumentParser

import redis
import uvicorn
from dodal.common.beamlines.beamline_parameters import (
    BEAMLINE_PARAMETER_PATHS,
    GDABeamlineParameters,
)
from fastapi import FastAPI

from . import __version__
from .constants import ENDPOINTS

__all__ = ["main"]


BEAMLINE_PARAM_PATH = ""
BEAMLINE_PARAMS: GDABeamlineParameters | None = None

app = FastAPI()
valkey = redis.Redis(host="localhost", port=6379, decode_responses=True)


@app.get(ENDPOINTS.BL_PARAM + "{item_id}")
def beamlineparameter(item_id: str):
    return {item_id: beamline_params.params.get(item_id)}


@app.post(ENDPOINTS.FEATURE + "{item_id}")
def set_featureflag(item_id: str, value: bool):
    return {"success": valkey.set(item_id, int(value))}


@app.get(ENDPOINTS.FEATURE + "{item_id}")
def get_featureflag(item_id: str):
    ret = valkey.get(item_id)
    return {item_id: bool(ret) if ret is not None else None}


def main():
    global BEAMLINE_PARAM_PATH
    global BEAMLINE_PARAMS
    parser = ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("-d", "--dev", action="store_true")
    args = parser.parse_args()
    if args.dev:
        BEAMLINE_PARAM_PATH = "tests/test_data/beamline_parameters.txt"
    else:
        BEAMLINE_PARAM_PATH = BEAMLINE_PARAMETER_PATHS["i03"]
    BEAMLINE_PARAMS = GDABeamlineParameters.from_file(BEAMLINE_PARAM_PATH)
    uvicorn.run(app="config_service.__main__:app", host="localhost", port=8000)


# test with: python -m config_service
if __name__ == "__main__":
    main()
