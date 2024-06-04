from dataclasses import dataclass


@dataclass(frozen=True)
class Endpoints:
    FEATURE = "/featureflag/"
    FEATURE_LIST = "/featurelist/"
    BL_PARAM = "/beamlineparameters/"


ENDPOINTS = Endpoints()
