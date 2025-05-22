from argparse import ArgumentParser

from . import __version__

__all__ = ["main"]

INSUFFICIENT_DEPENDENCIES_MESSAGE = "To do anything other than print the version and be\
    available for importing the client, you must install this package with [server]\
    optional dependencies"


def check_server_dependencies():
    try:
        import uvicorn  # noqa
        from fastapi import FastAPI  # noqa

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

        main()


# test with: python -m daq_config_server
if __name__ == "__main__":
    main()
