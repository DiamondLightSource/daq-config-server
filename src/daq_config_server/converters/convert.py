import json
from pathlib import Path
from typing import Any

import daq_config_server.converters._file_converter_map as file_converter_map
from daq_config_server.converters._converter_utils import ConverterParseError
from daq_config_server.converters.models import ConfigModel


def get_converted_file_contents(file_path: Path) -> dict[str, Any]:
    with file_path.open("r", encoding="utf-8") as f:
        raw_contents = f.read()
    if converter := file_converter_map.FILE_TO_CONVERTER_MAP.get(str(file_path)):
        try:
            contents = converter(raw_contents)
            if isinstance(contents, ConfigModel):
                return contents.model_dump()
            return contents
        except Exception as e:
            raise ConverterParseError(
                f"Unable to parse {str(file_path)} due to the following exception: \
                {type(e).__name__}: {e}"
            ) from e
    return json.loads(raw_contents)
