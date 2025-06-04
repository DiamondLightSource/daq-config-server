#!/bin/bash
TAG="dev"
PUSH=0
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
        -t|--tag)
            TAG="$2"
            shift
            echo "$TAG"
            ;;
        -p|--push)
            PUSH=1
            shift
            echo "Push the container to GCR."
            ;;
        -r|--run)
            shift
            echo "Run the container after building it."
            RUN_CONTAINER=1
            ;;
        -b|--rebuild)
            shift
            echo "Rebuild the container even if it already exists."
            REBUILD_CONTAINER=1

            ;;
        --help|--info|-h)
            echo "Build the current repository state as a container and optionally publish them to"
            echo "gcr.io/diamond-privreg/daq-config-server/<container-name>."
            echo " "
            echo "  -t, --tag <tag>       Specify the tag for the container. Default is 'dev'."
            echo "  -p, --push            Push the container to GCR. Requires a GitHub token, followed by"
            echo "                        podman login ghcr.io --username <your gh login> --password-stdin"
            echo "  -r, --run             Run the container after building it."
            echo "  -b, --rebuild         Rebuild the container even if it already exists."
            echo "  -h, --help, --info    Show this help message."    
            echo " "
            shift
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


MAIN_CONTAINER_NAME="${BASE_CONTAINER_NAME}"


MAIN_CONTAINER_TAG="${BASE_REPO_ADDR}${MAIN_CONTAINER_NAME}:${TAG}"

if [ -z "$(podman images -q $MAIN_CONTAINER_NAME:$TAG 2> /dev/null)" ] || [ $REBUILD_CONTAINER -gt 0 ]; then
    echo " "
    echo "========================================="
    echo "====           Building              ===="
    echo "========================================="
    echo " "
    echo "Building ${MAIN_CONTAINER_NAME}:${TAG}"
    echo " "
    podman build -t "${MAIN_CONTAINER_NAME}:${TAG}" .
else
    echo "Local image found, using existing image."
fi
rm .dockerignore
if [ $PUSH -gt 0 ]; then
    podman tag $MAIN_CONTAINER_NAME $MAIN_CONTAINER_TAG
    podman push $MAIN_CONTAINER_TAG $BASE_REPO_ADDR:$MAIN_CONTAINER_TAG
fi
if [ $RUN_CONTAINER -gt 0 ]; then
    echo "Running container ${MAIN_CONTAINER_NAME}:${TAG}..."
    # if the container is already running, stop it first
    if [ -n "$(podman ps -q --filter "name=$MAIN_CONTAINER_NAME")" ] ; then
        echo "Container $MAIN_CONTAINER_NAME is already running, stopping it first..."
        podman stop $MAIN_CONTAINER_NAME
    fi
    podman run -d -v ./tests/test_data:/tests/test_data:z --replace --name $MAIN_CONTAINER_NAME -p 8555:8555 "${MAIN_CONTAINER_NAME}:${TAG}"
fi
