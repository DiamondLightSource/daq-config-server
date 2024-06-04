import redis
import uvicorn
from dodal.common.beamlines.beamline_parameters import (
    BEAMLINE_PARAMETER_PATHS,
    GDABeamlineParameters,
)
from fastapi import FastAPI

from .constants import ENDPOINTS

app = FastAPI()
valkey = redis.Redis(host="localhost", port=6379, decode_responses=True)

__all__ = ["main"]

BEAMLINE_PARAM_PATH = ""
BEAMLINE_PARAMS: GDABeamlineParameters | None = None


@app.get(ENDPOINTS.BL_PARAM + "{item_id}")
def beamlineparameter(item_id: str):
    assert BEAMLINE_PARAMS is not None
    return {item_id: BEAMLINE_PARAMS.params.get(item_id)}


@app.post(ENDPOINTS.FEATURE + "{item_id}")
def set_featureflag(item_id: str, value: bool):
    return {"success": valkey.set(item_id, int(value))}


@app.get(ENDPOINTS.FEATURE + "{item_id}")
def get_featureflag(item_id: str):
    ret = int(valkey.get(item_id))  # type: ignore
    return {item_id: bool(ret) if ret is not None else None, "raw": ret}


def main(args):
    global BEAMLINE_PARAM_PATH
    global BEAMLINE_PARAMS
    if args.dev:
        BEAMLINE_PARAM_PATH = "tests/test_data/beamline_parameters.txt"
    else:
        BEAMLINE_PARAM_PATH = BEAMLINE_PARAMETER_PATHS["i03"]
    BEAMLINE_PARAMS = GDABeamlineParameters.from_file(BEAMLINE_PARAM_PATH)
    uvicorn.run(app="config_service.__main__:app", host="0.0.0.0", port=8555)
