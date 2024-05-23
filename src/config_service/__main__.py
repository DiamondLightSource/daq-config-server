import redis
from dodal.common.beamlines.beamline_parameters import (
    BEAMLINE_PARAMETER_PATHS,
    GDABeamlineParameters,
)
from fastapi import FastAPI

app = FastAPI()
r = redis.Redis(host="localhost", port=6379, decode_responses=True)
beamline_params = GDABeamlineParameters.from_file(BEAMLINE_PARAMETER_PATHS["i03"])


@app.get("/beamlineparameters/{item_id}")
def beamlineparameter(item_id: str):
    return {item_id: beamline_params.params.get(item_id)}


@app.post("/featureflag/{item_id}")
def set_featureflag(item_id: str, value):
    return {item_id: r.set(item_id, value)}


@app.get("/featureflag/{item_id}")
def get_featureflag(item_id: str):
    return {item_id: r.get(item_id)}
