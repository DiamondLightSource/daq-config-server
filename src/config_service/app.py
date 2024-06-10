import redis
import uvicorn
from dodal.common.beamlines.beamline_parameters import (
    BEAMLINE_PARAMETER_PATHS,
    GDABeamlineParameters,
)
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware

from .constants import ENDPOINTS

app = FastAPI()
origins = ["*"]  # TODO fix this
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


valkey = redis.Redis(host="localhost", port=6379, decode_responses=True)

__all__ = ["main"]

BEAMLINE_PARAM_PATH = ""
BEAMLINE_PARAMS: GDABeamlineParameters | None = None


@app.get(ENDPOINTS.BL_PARAM + "{item_id}")
def beamlineparameter(item_id: str):
    assert BEAMLINE_PARAMS is not None
    return {item_id: BEAMLINE_PARAMS.params.get(item_id)}


@app.post(ENDPOINTS.FEATURE + "{item_id}")
def set_featureflag(item_id: str, value: bool, response: Response):
    if not valkey.sismember(ENDPOINTS.FEATURE_LIST, item_id):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": f"Feature flag {item_id} does not exist!"}
    else:
        return {"success": valkey.set(item_id, int(value))}


@app.delete(ENDPOINTS.FEATURE + "{item_id}")
def delete_featureflag(item_id: str, response: Response):
    if not valkey.sismember(ENDPOINTS.FEATURE_LIST, item_id):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": f"Feature flag {item_id} does not exist!"}
    else:
        valkey.srem(ENDPOINTS.FEATURE_LIST, item_id)
        return {"success": not valkey.sismember(ENDPOINTS.FEATURE_LIST, item_id)}


@app.get(ENDPOINTS.FEATURE + "{item_id}")
def get_featureflag(item_id: str, response: Response):
    if not valkey.sismember(ENDPOINTS.FEATURE_LIST, item_id):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": f"Feature flag {item_id} does not exist!"}
    else:
        ret = int(valkey.get(item_id))  # type: ignore
        return {item_id: bool(ret) if ret is not None else None, "raw": ret}


@app.get(ENDPOINTS.FEATURE_LIST)
def get_featureflag_list():
    return valkey.smembers(ENDPOINTS.FEATURE_LIST)


@app.post(ENDPOINTS.FEATURE_LIST + "{item_id}", status_code=status.HTTP_201_CREATED)
def create_featureflag(item_id: str, response: Response):
    if valkey.sismember(ENDPOINTS.FEATURE_LIST, item_id):
        response.status_code = status.HTTP_409_CONFLICT
        return {"message": f"Feature flag {item_id} already exists!"}
    else:
        valkey.sadd(ENDPOINTS.FEATURE_LIST, item_id)
        return {"success": valkey.set(item_id, 0)}


def main(args):
    global BEAMLINE_PARAM_PATH
    global BEAMLINE_PARAMS
    if args.dev:
        BEAMLINE_PARAM_PATH = "tests/test_data/beamline_parameters.txt"
    else:
        BEAMLINE_PARAM_PATH = BEAMLINE_PARAMETER_PATHS["i03"]
    BEAMLINE_PARAMS = GDABeamlineParameters.from_file(BEAMLINE_PARAM_PATH)
    uvicorn.run(app="config_service.app:app", host="0.0.0.0", port=8555)
