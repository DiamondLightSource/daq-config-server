# The devcontainer should use the developer target and run as root with podman
# or docker with user namespaces.
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION} as developer

# Add any system dependencies for the developer/build environment here
RUN apt-get update && apt-get install -y --no-install-recommends \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Set up a virtual environment and put it in PATH
RUN python -m venv /venv
ENV PATH=/venv/bin:$PATH

# The build stage installs the context into the venv
FROM developer as build
COPY . /context
WORKDIR /context
RUN pip install .[server]

# The runtime stage copies the built venv into a slim runtime container
FROM python:${PYTHON_VERSION}-slim as runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*
COPY --from=build /venv/ /venv/
COPY tests/test_data/beamline_parameters.txt tests/test_data/beamline_parameters.txt
ENV PATH=/venv/bin:$PATH
ARG RUN_APP_IN_DEV_MODE=0
ENV DEV_MODE=${RUN_APP_IN_DEV_MODE}

# change this entrypoint if it is not the same as the repo
CMD config-service
