import logging
from abc import abstractmethod
from enum import StrEnum
from typing import Any, Self

from pydantic import model_validator

from daq_config_server.models import ConfigModel
from daq_config_server.models.converters._converter_utils import (
    parse_value,
    remove_comments,
)

LOGGER = logging.getLogger(__name__)


class FeatureSettingSources(StrEnum):
    # List of features and the name of that property in domain.properties
    @classmethod
    def to_dict(cls) -> dict[str, str]:
        return {member.value: member.name for member in cls}


class BaseFeatureSettings(ConfigModel):
    @model_validator(mode="before")
    @classmethod
    def _verify_features_against_sources(cls, data: Any) -> Any:
        sources_keys = {feature.name for feature in cls.feature_settings_sources()}
        feature_dc_keys = set(cls.model_fields)
        if sources_keys != feature_dc_keys:
            raise ValueError(
                "Model field names do not match source setting names: "
                f"{feature_dc_keys} != {sources_keys}"
            )
        return data

    @classmethod
    def from_domain_properties(cls, contents: str) -> Self:
        # From a domain.properties file
        lines = contents.splitlines()
        sources = cls.feature_settings_sources().to_dict()
        feature_settings: dict[str, Any] = {}
        for line in remove_comments(lines):
            setting, value = line.split("=", 1)
            if feature := sources.get(setting.strip()):
                feature_settings[feature] = parse_value(value)

        for gda_name, feature in sources.items():
            if feature not in feature_settings:
                LOGGER.warning(
                    f"Could not find {gda_name} in contents. "
                    f"Will use a default for {feature} if present."
                )
        return cls.model_validate(feature_settings)

    @staticmethod
    @abstractmethod
    def feature_settings_sources() -> type[FeatureSettingSources]: ...
