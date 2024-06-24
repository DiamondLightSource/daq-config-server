from dataclasses import dataclass


@dataclass(frozen=True)
class Endpoints:
    FEATURE = "/featureflag"
    FEATURE_DISALLOWED_SPECIALS = ["all"]
    BL_PARAM = "/beamlineparameters"
    INFO = "/info"


@dataclass(frozen=True)
class DatabaseKeys:
    FEATURE_SET = "featureflags"


DATABASE_KEYS = DatabaseKeys()
ENDPOINTS = Endpoints()
