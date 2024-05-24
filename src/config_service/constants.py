from dataclasses import dataclass


@dataclass(frozen=True)
class Endpoints:
    FEATURE = "/featureflag/"
    BL_PARAM = "/beamlineparameters/"


ENDPOINTS = Endpoints()
