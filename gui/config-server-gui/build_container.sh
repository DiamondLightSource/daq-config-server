#!/bin/bash

module load node
npm run build
podman build -t daq-config-server-gui .
podman push daq-config-server-gui gcr.io/diamond-privreg/daq-config-server/daq-config-server-gui
