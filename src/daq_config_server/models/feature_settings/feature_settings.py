import logging
from abc import abstractmethod
from enum import StrEnum
from typing import Any, Self

from daq_config_server.models.base_model import ConfigModel
from daq_config_server.models.utils import parse_value, remove_comments

LOGGER = logging.getLogger(__name__)


class FeatureSettingSources(StrEnum):
    ...

    # List of features and the name of that property in domain.properties
    @classmethod
    def to_dict(cls) -> dict[str, str]:
        return {member.name: member.value for member in cls}


class BaseFeatureSettings(ConfigModel):
    @classmethod
    def from_contents(cls, contents: str) -> Self:
        lines = contents.splitlines()
        sources = cls.feature_settings_sources().to_dict()
        settings: dict[str, Any] = {}
        pairs: list[tuple[str, str]] = []
        for line in remove_comments(lines):
            setting, value = line.split("=", 1)
            pairs.append((setting.strip(), value.strip()))

        for key, setting_name in sources.items():
            for setting, value in pairs:
                if setting_name == setting.strip():
                    settings[key] = parse_value(value)
                    break
            if key not in settings:
                LOGGER.warning(
                    f"Could not find {setting_name} in file. "
                    f"Will use a default for {key} if present"
                )

        return cls.model_validate(settings)

    @classmethod
    @abstractmethod
    def feature_settings_sources(cls) -> type[FeatureSettingSources]:
        raise NotImplementedError("Define a method to get feature settings sources")
