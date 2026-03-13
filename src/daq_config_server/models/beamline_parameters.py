import ast
from typing import Any

from daq_config_server.models.utils import remove_comments

ALLOWED_BEAMLINE_PARAMETER_STRINGS = ["FB", "FULL", "deadtime"]


def _parse_value(
    value: str,
) -> Any:
    replacements = {"yes": "True", "no": "False", "true": "True", "false": "False"}
    return ast.literal_eval(replacements.get(value.lower(), value))


def beamline_parameters_to_dict(contents: str) -> dict[str, Any]:
    """Extracts the key value pairs from a beamline parameters file. If the value
    is in ALLOWED_BEAMLINE_PARAMETER_STRINGS, it leaves it as a string. Otherwise, it is
    converted to a number or bool."""
    lines = contents.splitlines()
    config_pairs: dict[str, Any] = {}

    # Get dict of parameter keys and values
    for line in remove_comments(lines):
        splitline = line.split("=")
        if len(splitline) >= 2:
            param, value = line.split("=")
            if param.strip() in config_pairs:
                raise ValueError(f"Repeated key in parameters: {param}")
            config_pairs[param.strip()] = value.strip()

    # Parse each value
    for param, value in config_pairs.items():
        if value not in ALLOWED_BEAMLINE_PARAMETER_STRINGS:
            config_pairs[param] = _parse_value(value)
    return dict(config_pairs)
