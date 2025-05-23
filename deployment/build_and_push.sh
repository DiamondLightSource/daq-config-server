#!/bin/bash

DEV=0
PUSH=1

for option in "$@"; do
    case $option in
        -d|--dev)
            DEV=1
            ;;
        -n|--no-push)
            PUSH=0
            ;;
        --help|--info|--h)
            echo "Build and push the current repository state into containers and publish them to"
            echo "gcr.io/diamond-privreg/daq-config-server/<container-name> ready for deployment."
            echo " "
            echo "  -d, --dev       Creates -dev:latest tagged containers for testing on argus."
            echo "  -n, --no-push   Don't push containers to GCR."
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

echo " "
echo "========================================="
echo "====  Building and pushing main app  ===="
echo "========================================="
echo " "
echo "Building ${MAIN_CONTAINER_NAME}"
echo " "
podman build --build-arg -t $MAIN_CONTAINER_NAME .
if [ $PUSH -gt 0 ]; then
    podman tag $MAIN_CONTAINER_NAME $MAIN_CONTAINER_TAG
    podman push $MAIN_CONTAINER_NAME $MAIN_CONTAINER_TAG
fi
