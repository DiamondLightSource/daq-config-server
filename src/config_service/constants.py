from dataclasses import dataclass


@dataclass(frozen=True)
class Endpoints:
    FEATURE = "/featureflag"
    FEATURE_LIST = "/featurelist"
    BL_PARAM = "/beamlineparameters"
    INFO = "/info"


ENDPOINTS = Endpoints()
