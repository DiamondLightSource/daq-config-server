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
            echo "  -d, --dev       Creates -dev:latest tagged containers for testing on pollux."
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
    GUI_CONTAINER_NAME="${BASE_CONTAINER_NAME}-gui-dev"
    DB_CONTAINER_NAME="${BASE_CONTAINER_NAME}-db-dev"
else
    echo "Building prod-mode containers..."
    MAIN_CONTAINER_NAME="${BASE_CONTAINER_NAME}"
    GUI_CONTAINER_NAME="${BASE_CONTAINER_NAME}-gui"
    DB_CONTAINER_NAME="${BASE_CONTAINER_NAME}-db"
fi
echo " "

MAIN_CONTAINER_TAG="${BASE_REPO_ADDR}${MAIN_CONTAINER_NAME}"
GUI_CONTAINER_TAG="${BASE_REPO_ADDR}${GUI_CONTAINER_NAME}"
DB_CONTAINER_TAG="${BASE_REPO_ADDR}${DB_CONTAINER_NAME}"

# set env vars which will be used by build process:
if [ $DEV -gt 0 ]; then
    export REACT_APP_BACKEND_ADDR="http://localhost:8855"
    export MAIN_APP_DEV_MODE=1
else
    export REACT_APP_BACKEND_ADDR="https://daq-config.diamond.ac.uk/api"
    export MAIN_APP_DEV_MODE=0
fi

echo " "
echo "========================================="
echo "====  Building and pushing main app  ===="
echo "========================================="
echo " "
echo "Building ${MAIN_CONTAINER_NAME}"
echo " "
podman build --build-arg RUN_APP_IN_DEV_MODE=$MAIN_APP_DEV_MODE -t $MAIN_CONTAINER_NAME .
if [ $PUSH -gt 0 ]; then
    podman tag $MAIN_CONTAINER_NAME $MAIN_CONTAINER_TAG
    podman push $MAIN_CONTAINER_NAME $MAIN_CONTAINER_TAG
fi

cd gui/config-server-gui

echo " "
echo "========================"
echo "====  Building GUI  ===="
echo "========================"
module load node
npm run build

echo " "
echo "=============================================="
echo "====  Building and pushing GUI container  ===="
echo "=============================================="
echo " "
echo "Building ${GUI_CONTAINER_NAME}"
echo " "
podman build -t $GUI_CONTAINER_NAME .
if [ $PUSH -gt 0 ]; then
    podman tag $GUI_CONTAINER_NAME $GUI_CONTAINER_TAG
    podman push $GUI_CONTAINER_NAME $GUI_CONTAINER_TAG
fi

cd ../../valkey

echo " "
echo "============================================="
echo "====  Building and pushing DB container  ===="
echo "============================================="
echo " "
echo "Building ${DB_CONTAINER_NAME}"
echo " "
podman build -t $DB_CONTAINER_NAME .
if [ $PUSH -gt 0 ]; then
    podman tag $DB_CONTAINER_NAME $DB_CONTAINER_TAG
    podman push $DB_CONTAINER_NAME $DB_CONTAINER_TAG
fi