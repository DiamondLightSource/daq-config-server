import json
from pathlib import Path
from typing import Any

from daq_config_server.models._base_model import ConfigModel

from ._file_converter_map import FILE_TO_CONVERTER_MAP


class ConverterParseError(Exception): ...


def get_converted_file_contents(file_path: Path) -> dict[str, Any]:
    with file_path.open("r", encoding="utf-8") as f:
        raw_contents = f.read()
    if converter := FILE_TO_CONVERTER_MAP.get(str(file_path)):
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
