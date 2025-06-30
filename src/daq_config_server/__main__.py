"""Interface for ``python -m daq_config_server``."""

from argparse import ArgumentParser

from . import __version__
from .app import main as main_app

__all__ = ["main"]


def main():
    parser = ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.parse_args()
    main_app()


if __name__ == "__main__":
    main()
