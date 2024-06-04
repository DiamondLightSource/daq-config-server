from argparse import ArgumentParser

from . import __version__

try:
    import redis  # noqa
    import uvicorn  # noqa
    from fastapi import FastAPI  # noqa

    server_dependencies_exist = True
except ImportError:
    server_dependencies_exist = False


__all__ = ["main"]


def main():
    parser = ArgumentParser()
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("-d", "--dev", action="store_true")
    args = parser.parse_args()
    if not server_dependencies_exist:
        print(
            "To do anything other than print the version and be available for "
            "importing the client, you must install this package with [server] "
            "optional dependencies"
        )
    else:
        from .app import main

        main(args)


# test with: python -m config_service
if __name__ == "__main__":
    main()
