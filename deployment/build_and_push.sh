#!/bin/bash

DEV=0
PUSH=1
RUN_CONTAINER=0
REBUILD_CONTAINER=0

cd -- "$( dirname -- "$BASH_SOURCE[0]" )"
cd ..
# make dockerignore from .gitignore
if [ ! -f .gitignore ]; then
    echo "No .gitignore file found, exiting."
    exit 1
fi

cp .gitignore .dockerignore
for option in "$@"; do
    case $option in
        -d|--dev)
            DEV=1
            ;;
        -n|--no-push)
            PUSH=0
            ;;
        -r|--run)
            echo "Run the container after building it."
            RUN_CONTAINER=1
            ;;
        -b|--rebuild)
            echo "Rebuild the container even if it already exists."
            REBUILD_CONTAINER=1

            ;;
        --help|--info|--h)
            echo "Build and push the current repository state into containers and publish them to"
            echo "gcr.io/diamond-privreg/daq-config-server/<container-name> ready for deployment."
            echo " "
            echo "  -d, --dev       Creates -dev:latest tagged containers for testing on argus."
            echo "  -n, --no-push   Don't push containers to GCR."
            echo "  -r, --run       Run the container after building it."
            echo "  -b, --rebuild   Rebuild the container even if it already exists."
            echo "  --help, --info, -h  Show this help message."    
            echo " "
            exit 0
            ;;

        -*|--*)
            echo "Unknown option ${option}. Use --help for info on option usage."
            exit 1
            ;;
    esac
done

# set container and tag names:
BASE_CONTAINER_NAME="daq-config-server"
BASE_REPO_ADDR="gcr.io/diamond-privreg/daq-config-server/"
if [ $DEV -gt 0 ]; then
    echo "Building dev-mode containers..."
    MAIN_CONTAINER_NAME="${BASE_CONTAINER_NAME}-dev"
else
    echo "Building prod-mode containers..."
    MAIN_CONTAINER_NAME="${BASE_CONTAINER_NAME}"
fi
echo " "

MAIN_CONTAINER_TAG="${BASE_REPO_ADDR}${MAIN_CONTAINER_NAME}"

# set env vars which will be used by build process:
if [ $DEV -gt 0 ]; then
    export REACT_APP_BACKEND_ADDR="http://localhost:8555"
else
    export REACT_APP_BACKEND_ADDR="https://daq-config.diamond.ac.uk/api"
fi
if [ -z "$(podman images -q $MAIN_CONTAINER_NAME 2> /dev/null)" ] || [ $REBUILD_CONTAINER -gt 0 ]; then
    echo " "
    echo "========================================="
    echo "====           Building              ===="
    echo "========================================="
    echo " "
    echo "Building ${MAIN_CONTAINER_NAME}"
    echo " "
    podman build -t $MAIN_CONTAINER_NAME .
else
    echo "Local image found, using existing image."
fi
rm .dockerignore
if [ $PUSH -gt 0 ]; then
    podman tag $MAIN_CONTAINER_NAME $MAIN_CONTAINER_TAG
    podman push $MAIN_CONTAINER_NAME $MAIN_CONTAINER_TAG
fi
if [ $RUN_CONTAINER -gt 0 ]; then
    echo "Running container ${MAIN_CONTAINER_NAME}..."
    # if the container is already running, stop it first
    if podman ps -q --filter "name=$MAIN_CONTAINER_NAME" > /dev/null; then
        echo "Container $MAIN_CONTAINER_NAME is already running, stopping it first..."
        podman stop $MAIN_CONTAINER_NAME
    fi
    podman run -d -v /dls_sw/:/dls_sw/ -v ./tests/test_data:/tests/test_data:z --replace --name $MAIN_CONTAINER_NAME -p 8555:8555 $MAIN_CONTAINER_NAME
fi
