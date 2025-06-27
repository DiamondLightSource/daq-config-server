[![Frontend CI](https://github.com/DiamondLightSource/daq-config-server/actions/workflows/gui_ci.yml/badge.svg)](https://github.com/DiamondLightSource/daq-config-server/actions/workflows/gui_ci.yml)
[![Backend CI](https://github.com/DiamondLightSource/daq-config-server/actions/workflows/ci.yml/badge.svg)](https://github.com/DiamondLightSource/daq-config-server/actions/workflows/backend_ci.yml)
[![Coverage](https://codecov.io/gh/DiamondLightSource/daq-config-server/branch/main/graph/badge.svg)](https://codecov.io/gh/DiamondLightSource/daq-config-server)
[![PyPI](https://img.shields.io/pypi/v/daq-config-server.svg)](https://pypi.org/project/daq-config-server)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

# DAQ Config Server

A service to read files on Diamond's filesystem from a BlueAPI container. Currently this service is only able to read files on `/dls_sw/`. Writing to configuration files will come in a future release.

|  Source  |     <https://github.com/DiamondLightSource/daq-config-server>      |
| :------: | :----------------------------------------------------------------: |
|  Docker  |  `docker run ghcr.io/DiamondLightSource/daq-config-server:latest`  |
| Releases | <https://github.com/DiamondLightSource/daq-config-server/releases> |

Here is a minimal example to read a file from the centrally hosted service after installing this package

```python
from daq_config_server.client import ConfigServer

config_server = ConfigServer("https://daq-config.diamond.ac.uk")

file_contents = config_server.get_file_contents({ABSOLUTE_PATH_TO_CONFIG_FILE}, desired_return_type=str)

```
The output will come out as a raw string - you should format it as required in your own code. You may also request that the file contents is returned as a `dict` or in `bytes` - this will raise an http exception if the file cannot be converted to that type. To be able to read a file, you must first add it to the [whitelist](https://github.com/DiamondLightSource/daq-config-server/blob/main/whitelist.yaml).


## Testing and deployment

To run unit tests, type `tox -e unit_tests` from within the dev container

There is a convenient script in `./deployment/build_and_push.sh` which can be used to easily build and run the container locally for testing, and optionally push the container to ghcr. In general we should rely on the CI to be pushing new containers - it should only be done manually for urgent debugging.

To run system tests, start a local container by running `./deployment/build_and_push.sh -r -b`. Then, in the dev container, forward port 8555. There are instructions on port forwarding within vscode [here](https://code.visualstudio.com/docs/debugtest/port-forwarding). Next, in a terminal in the devcontainer, run `pytest .` from the `daq-config-server` directory.

To test on argus, log in to argus in your namespace and run:

```bash
helm install daq-config ./helmchart/ --values dev-values.yaml
```

followed by:

```bash
kubectl port-forward service/daq-config-server-svc 8555
```

after which you should be able to access the API on `http://localhost:8555/docs`

<!-- README only content. Anything below this line won't be included in index.md -->
