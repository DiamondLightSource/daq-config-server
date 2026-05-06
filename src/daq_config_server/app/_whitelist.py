import atexit
import logging
import time
from pathlib import Path
from threading import Event, Thread

import yaml

from daq_config_server.app._config import WhitelistConfig

LOGGER = logging.getLogger(__name__)


WHITELIST_REFRESH_RATE_S = 300

_whitelist: "FilesystemWhitelist"


class FilesystemWhitelist:
    """Read the whitelist from a configuration file, and check for
    updates every 5 minutes. This lets the deployed server see updates to the whitelist
    without requiring a new release or a restart"""

    def __init__(self, path: Path):
        self._path = path
        self._initial_load()
        self._stop = Event()
        self.update_in_background_thread = Thread(
            target=self._periodically_update_whitelist, daemon=True
        )
        self.update_in_background_thread.start()

    def _fetch(self) -> str:
        """Read the whitelist from a configuration file.
        Returns:
            str: The whitelist YAML
        """
        with self._path.open() as f:
            return f.read()

    def _fetch_and_update(self):
        text = self._fetch()
        data = yaml.safe_load(text)
        self.whitelist_files = {Path(p) for p in data.get("whitelist_files")}
        self.whitelist_dirs = {Path(p) for p in data.get("whitelist_dirs")}

    def _initial_load(self):
        try:
            self._fetch_and_update()
            LOGGER.info("Successfully read whitelist.")
        except Exception as e:
            LOGGER.error(f"Initial whitelist load failed: {e}")
            raise RuntimeError("Failed to load whitelist during initialization.") from e

    def _periodically_update_whitelist(self):
        while not self._stop.is_set():
            time.sleep(WHITELIST_REFRESH_RATE_S)
            try:
                self._fetch_and_update()
                LOGGER.info("Whitelist updated successfully.")
            except Exception as e:
                LOGGER.error(f"Failed to update whitelist: {e}")

    def stop(self):
        self._stop.set()
        self.update_in_background_thread.join(timeout=1)


def get_whitelist() -> FilesystemWhitelist:
    return _whitelist


def init_whitelist(config: WhitelistConfig) -> None:
    global _whitelist
    _whitelist = FilesystemWhitelist(Path(config.config_file))
    atexit.register(_whitelist.stop)


def path_is_whitelisted(file_path: Path) -> bool:
    whitelist = get_whitelist()
    return file_path in whitelist.whitelist_files or any(
        file_path.is_relative_to(dir) for dir in whitelist.whitelist_dirs
    )
