from os import environ

import strawberry
import uvicorn
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from redis import Redis
from strawberry.fastapi import GraphQLRouter

from .beamline_parameters import (
    BEAMLINE_PARAMETER_PATHS,
    GDABeamlineParameters,
)
from .constants import DATABASE_KEYS, ENDPOINTS

BEAMLINE_PARAM_PATH = ""
BEAMLINE_PARAMS: GDABeamlineParameters | None = None
DEV_MODE = bool(int(environ.get("DEV_MODE") or 0))


@strawberry.type
class BeamlineParameter:
    key: str
    value: str | None  # Some parameters may be None


@strawberry.type
class FeatureFlag:
    name: str
    value: bool


@strawberry.type
class Query:
    @strawberry.field
    def beamline_parameter(self, key: str) -> BeamlineParameter | None:
        """Fetch a single beamline parameter"""
        if BEAMLINE_PARAMS is None:
            return None

        value = BEAMLINE_PARAMS.params.get(key)
        if value is None:
            return None
        return BeamlineParameter(key=key, value=value)

    @strawberry.field
    def all_beamline_parameters(
        self, keys: list[str] | None = None
    ) -> list[BeamlineParameter]:
        """Fetch multiple beamline parameters (all or filtered)"""
        if BEAMLINE_PARAMS is None:
            return []
        if keys is None:
            return [
                BeamlineParameter(key=k, value=v)
                for k, v in BEAMLINE_PARAMS.params.items()
            ]
        return [
            BeamlineParameter(key=k, value=BEAMLINE_PARAMS.params.get(k))
            for k in keys
            if k in BEAMLINE_PARAMS.params
        ]

    @strawberry.field
    def feature_flags(self, get_values: bool = False) -> list[FeatureFlag]:
        """Get all feature flags (as names or with values)"""
        flags = valkey.smembers("feature_flags")  # Set name in Redis
        if not get_values:
            return [
                FeatureFlag(name=flag, value=False) for flag in flags
            ]  # Only names, values ignored
        return [
            FeatureFlag(name=flag, value=bool(int(valkey.get(flag)))) for flag in flags
        ]


graphql_schema = strawberry.Schema(query=Query)
ROOT_PATH = "/api"
print(f"{DEV_MODE=}")
print(f"{ROOT_PATH=}")
if DEV_MODE:
    print("Running in dev mode! not setting root path!")
    ROOT_PATH = ""

app = FastAPI(
    title="DAQ config server",
    description="""For storing and fetching beamline parameters, etc. which are needed
    by more than one applicatioon or service""",
    root_path=ROOT_PATH,
)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
graphql_app = GraphQLRouter(graphql_schema)
app.include_router(graphql_app, prefix="/graphql")

valkey = Redis(host="localhost", port=6379, decode_responses=True)
__all__ = ["main"]


@app.get(ENDPOINTS.BL_PARAM + "/{param}")
def get_beamline_parameter(param: str):
    """Get a single beamline parameter"""
    assert BEAMLINE_PARAMS is not None
    return {param: BEAMLINE_PARAMS.params.get(param)}


class ParamList(BaseModel):
    param_list: list[str]


@app.get(ENDPOINTS.BL_PARAM)
def get_all_beamline_parameters(param_list_data: ParamList | None = None):
    """Get a dict of all the current beamline parameters."""
    assert BEAMLINE_PARAMS is not None
    if param_list_data is None:
        return BEAMLINE_PARAMS.params
    return {k: BEAMLINE_PARAMS.params.get(k) for k in param_list_data.param_list}


@app.get(ENDPOINTS.FEATURE)
def get_feature_flag_list(get_values: bool = False):
    """Get a list of all the current feature flags, or a dict of all the current values
    if get_values=true is passed"""
    flags = valkey.smembers(DATABASE_KEYS.FEATURE_SET)
    if not get_values:
        return flags
    else:
        return {flag: bool(int(valkey.get(flag))) for flag in flags}  # type: ignore


@app.get(ENDPOINTS.FEATURE + "/{flag_name}")
def get_feature_flag(flag_name: str, response: Response):
    """Get the value of a feature flag"""
    if not valkey.sismember(DATABASE_KEYS.FEATURE_SET, flag_name):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": f"Feature flag {flag_name} does not exist!"}
    else:
        ret = int(valkey.get(flag_name))  # type: ignore # We checked if it exists above
        return {flag_name: bool(ret)}


@app.post(ENDPOINTS.FEATURE + "/{flag_name}", status_code=status.HTTP_201_CREATED)
def create_feature_flag(flag_name: str, response: Response, value: bool = False):
    """Sets a feature flag, creating it if it doesn't exist. Default to False."""
    if valkey.sismember(DATABASE_KEYS.FEATURE_SET, flag_name):
        response.status_code = status.HTTP_409_CONFLICT
        return {"message": f"Feature flag {flag_name} already exists!"}
    else:
        valkey.sadd(DATABASE_KEYS.FEATURE_SET, flag_name)
        return {"success": valkey.set(flag_name, int(value))}


@app.put(ENDPOINTS.FEATURE + "/{flag_name}")
def set_feature_flag(flag_name: str, value: bool, response: Response):
    """Sets a feature flag, return an error if it doesn't exist."""
    if not valkey.sismember(DATABASE_KEYS.FEATURE_SET, flag_name):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": f"Feature flag {flag_name} does not exist!"}
    else:
        return {"success": valkey.set(flag_name, int(value))}


@app.delete(ENDPOINTS.FEATURE + "/{flag_name}")
def delete_feature_flag(flag_name: str, response: Response):
    """Delete a feature flag."""
    if not valkey.sismember(DATABASE_KEYS.FEATURE_SET, flag_name):
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": f"Feature flag {flag_name} does not exist!"}
    else:
        valkey.srem(DATABASE_KEYS.FEATURE_SET, flag_name)
        return {"success": not valkey.sismember(DATABASE_KEYS.FEATURE_SET, flag_name)}


@app.get(ENDPOINTS.INFO)
def get_info(request: Request):
    """Get some generic information about the request, mostly for debugging"""
    return {
        "message": "Welcome to daq-config API.",
        "root_path": request.scope.get("root_path"),
        "request_headers": request.headers,
    }


if DEV_MODE:

    @app.api_route("/{full_path:path}")
    async def catch_all(request: Request, full_path: str):
        return {
            "message": "resource not found, supplying info for debug",
            "root_path": request.scope.get("root_path"),
            "path": full_path,
            "request_headers": repr(request.headers),
        }


def _load_beamline_params():
    global BEAMLINE_PARAMS
    BEAMLINE_PARAMS = GDABeamlineParameters.from_file(BEAMLINE_PARAM_PATH)


def _set_beamline_param_path(dev: bool = True):
    global BEAMLINE_PARAM_PATH
    if dev:
        BEAMLINE_PARAM_PATH = "tests/test_data/beamline_parameters.txt"
    else:
        BEAMLINE_PARAM_PATH = BEAMLINE_PARAMETER_PATHS["i03"]


def main(args):
    _set_beamline_param_path(args.dev)
    _load_beamline_params()
    uvicorn.run(app="daq_config_server.app:app", host="0.0.0.0", port=8555)
