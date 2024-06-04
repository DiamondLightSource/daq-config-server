from argparse import ArgumentParser

from fastapi import dependencies

from . import __version__
from .constants import ENDPOINTS

try:
    import redis
    import uvicorn
    from dodal.beamlines.beamline_parameters import (
        BEAMLINE_PARAMETER_PATHS,
        GDABeamlineParameters,
    )
    from fastapi import FastAPI

    app = FastAPI()
    valkey = redis.Redis(host="localhost", port=6379, decode_responses=True)

    server_dependencies_exist = True
except ImportError:
    server_dependencies_exist = False

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


def main():
    global BEAMLINE_PARAM_PATH
    global BEAMLINE_PARAMS
    parser = ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("-d", "--dev", action="store_true")
    args = parser.parse_args()
    if not server_dependencies_exist:
        print(
            "To do anything other than print the version and be available for "
            "importing the client, you must install this package with [server] "
            "optional dependencies"
        )
    if args.dev:
        BEAMLINE_PARAM_PATH = "tests/test_data/beamline_parameters.txt"
    else:
        BEAMLINE_PARAM_PATH = BEAMLINE_PARAMETER_PATHS["i03"]
    BEAMLINE_PARAMS = GDABeamlineParameters.from_file(BEAMLINE_PARAM_PATH)
    uvicorn.run(app="config_service.__main__:app", host="0.0.0.0", port=8555)


# test with: python -m config_service
if __name__ == "__main__":
    main()
