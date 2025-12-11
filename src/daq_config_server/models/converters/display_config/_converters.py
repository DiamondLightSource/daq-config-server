from daq_config_server.models.converters import parse_value, remove_comments

from ._models import DisplayConfig, DisplayConfigData


def display_config_to_model(contents: str) -> DisplayConfig:
    lines = contents.splitlines()
    config_dict: dict[float, dict[str, int | float]] = {}
    zoom_level = None

    for line in remove_comments(lines):
        key, value = (item.strip() for item in line.split("=", 1))
        if key == "zoomLevel":
            zoom_level = float(value)
            assert zoom_level not in config_dict.keys(), (
                f"Multiple instances of zoomLevel {zoom_level}"
            )
            config_dict[zoom_level] = {}
            continue

        assert zoom_level is not None, "File must start with a zoom level"
        assert key not in config_dict[zoom_level].keys(), (
            "File can't have repeated keys for a given zoom level"
        )
        config_dict[zoom_level][key] = parse_value(value)
    zoom_levels = {
        key: DisplayConfigData.model_validate(value)
        for key, value in config_dict.items()
    }

    return DisplayConfig(zoom_levels=zoom_levels)
