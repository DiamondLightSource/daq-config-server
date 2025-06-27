"""Interface for ``python -m daq_config_server``."""

import os
from argparse import ArgumentParser

import yaml

from daq_config_server.log import LoggingConfig, set_up_logging

from . import __version__

__all__ = ["main"]

CONFIG_PATH = "/etc/config/config.yaml"

INSUFFICIENT_DEPENDENCIES_MESSAGE = "To do anything other than print the version and be\
    available for importing the client, you must install this package with [server]\
    optional dependencies"


def check_server_dependencies():
    try:
        import uvicorn  # type: ignore  # noqa: F401
        from fastapi import FastAPI  # type: ignore # noqa

        return True

    except ImportError:
        return False


def main():
    parser = ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.parse_args()

    if not check_server_dependencies():
        print(INSUFFICIENT_DEPENDENCIES_MESSAGE)
    else:
        from .app import main

        # Set up logging with defaults, or using config.yaml if it exists
        if os.path.isfile(CONFIG_PATH):
            with open(CONFIG_PATH) as f:
                data = yaml.safe_load(f)
                logging_config = LoggingConfig(**data)
        else:
            logging_config = LoggingConfig()

        set_up_logging(logging_config)
        main()


if __name__ == "__main__":
    main()
