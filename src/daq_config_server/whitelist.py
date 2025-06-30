import atexit
import logging
import time
from functools import cache
from pathlib import Path
from threading import Event, Thread

import requests
import yaml

from daq_config_server.constants import (
    WHITELIST_REFRESH_RATE_S,
    WHITELIST_URL,
)

LOGGER = logging.getLogger(__name__)


class WhitelistFetcher:
    """Read the whitelist from the main branch of this repo from github, and check for
    updates every 5 minutes. This lets the deployed server see updates to the whitelist
    without requiring a new release or a restart"""

    def __init__(self):
        self._initial_load()
        self._stop = Event()
        self.update_in_background_thread = Thread(
            target=self._periodically_update_whitelist, daemon=True
        )
        self.update_in_background_thread.start()

    def _fetch_and_update(self):
        response = requests.get(WHITELIST_URL)
        response.raise_for_status()
        data = yaml.safe_load(response.text)
        self.whitelist_files = {Path(p) for p in data.get("whitelist_files")}
        self.whitelist_dirs = {Path(p) for p in data.get("whitelist_dirs")}

    def _initial_load(self):
        try:
            self._fetch_and_update()
            LOGGER.info("Successfully read whitelist from GitHub.")
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


@cache
def get_whitelist() -> WhitelistFetcher:
    fetcher = WhitelistFetcher()
    atexit.register(fetcher.stop)
    return fetcher
