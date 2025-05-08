from argparse import ArgumentParser

from . import __version__

try:
    import uvicorn  # noqa
    from fastapi import FastAPI  # noqa

    server_dependencies_exist = True
except ImportError:
    server_dependencies_exist = False


__all__ = ["main"]


def main():
    parser = ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.parse_args()

    if not server_dependencies_exist:
        print(
            "To do anything other than print the version and be available for "
            "importing the client, you must install this package with [server] "
            "optional dependencies"
        )
    else:
        from .app import main

        main()


# test with: python -m daq_config_server
if __name__ == "__main__":
    main()
