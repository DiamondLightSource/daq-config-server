import logging
from abc import abstractmethod
from enum import StrEnum
from typing import Any, Self

from daq_config_server.models.base_model import ConfigModel
from daq_config_server.models.utils import parse_value, remove_comments

LOGGER = logging.getLogger(__name__)


class FeatureSettingSources(StrEnum):
    # List of features and the name of that property in domain.properties
    @classmethod
    def to_dict(cls) -> dict[str, str]:
        return {member.name: member.value for member in cls}


class BaseFeatureSettings(ConfigModel):
    @classmethod
    def from_domain_properties(cls, contents: str) -> Self:
        # From a domain.properties file
        lines = contents.splitlines()
        sources = cls.feature_settings_sources().to_dict()
        pairs: list[tuple[str, str]] = []
        for line in remove_comments(lines):
            setting, value = line.split("=", 1)
            pairs.append((setting.strip(), value.strip()))

        feature_settings: dict[str, Any] = {}
        for feature, gda_name in sources.items():
            for setting, value in pairs:
                if gda_name == setting:
                    feature_settings[feature] = parse_value(value)
                    break
            if feature not in feature_settings:
                LOGGER.warning(
                    f"Could not find {gda_name} in contents. "
                    f"Will use a default for {feature} if present."
                )
        return cls.model_validate(feature_settings)

    @staticmethod
    @abstractmethod
    def feature_settings_sources() -> type[FeatureSettingSources]:
        raise NotImplementedError("Define a method to get feature settings sources")
