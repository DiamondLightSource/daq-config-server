[![Frontend CI](https://github.com/DiamondLightSource/daq-config-server/actions/workflows/gui_ci.yml/badge.svg)](https://github.com/DiamondLightSource/daq-config-server/actions/workflows/gui_ci.yml)
[![Backend CI](https://github.com/DiamondLightSource/daq-config-server/actions/workflows/backend_ci.yml/badge.svg)](https://github.com/DiamondLightSource/daq-config-server/actions/workflows/backend_ci.yml)
[![Coverage](https://codecov.io/gh/DiamondLightSource/daq-config-server/branch/main/graph/badge.svg)](https://codecov.io/gh/DiamondLightSource/daq-config-server)
[![PyPI](https://img.shields.io/pypi/v/daq-config-server.svg)](https://pypi.org/project/daq-config-server)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# DAQ Config Server

A service to put and get your config values from.

Comprises a FastAPI backend with a valkey database to C/R/U/D config values, and a Chakra/React frontend for easier management.

Currently the scope is JUST storing and retrieving feature flags for Hyperion/I03 UDC but we hope to expand this to replace all DAQ config files.

|  Source  |     <https://github.com/DiamondLightSource/daq-config-server>      |
| :------: | :----------------------------------------------------------------: |
|  Docker  |  `docker run ghcr.io/DiamondLightSource/daq-config-server:latest`  |
| Releases | <https://github.com/DiamondLightSource/daq-config-server/releases> |

A simple app for storing and fetching values. Has a Valkey (Redis) instance as well as options for file-backed legacy
values (e.g. `beamlineParameters`...)

Currently the server application always needs to be run with the `--dev` flag, as it cannot yet look at the DLS
filesystem to find the real beamline parameter files.

To use the config values in an experimental application (e.g. Hyperion) you can do:

```python
from daq_config_server.client import ConfigServer

config_server = ConfigServer("<service ip address>", <port>)

use_stub_offsets: bool = config_server.best_effort_get_feature_flag("use_stub_offsets")

```

To work on the GUI you will probably need to run:

```bash
module load node
npm install
```

in the gui directory to setup the environment.

## Testing and deployment

There is a convenient script in `./deployment/build_and_push_all.sh` to build all the containers, which takes
a `--dev` option to push containers with `-dev` appended to their names and a `--no-push` option for local
development. This ensures that environment variables for dev or prod builds are included in the built container,
such as the GUI pointing at the subdomain URL vs. localhost, and the `root_path` of the FastAPI app. To push to
the registry you must have identified to gcloud by having loaded a kubernetes module and running `gcloud auth login.`

To deploy a live version, you can run the above script with no arguments and then while logged in to
argus, in the `daq-config-server` namespace, run `kubectl rollout restart deployment`. If it is not
currently deploy it you can deploy it with `helm install daq-config ./helmchart`.

To test locally, you can build everything with `./deployment/build_and_push_all.sh --dev --no-push` and then
run the containers `daq-config-server-dev` (with the command `daq-config-server --dev`), `daq-config-server-db-dev`,
and `daq-config-server-gui-dev`, all with the `--net host` option.

To test on pollux, log in to pollux in your namespace and run:

```bash
helm install daq-config ./helmchart/ --values dev-values.yaml
```

followed by:

```bash
kubectl port-forward service/daq-config-server-svc 8080 8555
```

after which you should be able to access the frontend on `http://localhost:8080` and the API on `http://localhost:8555`
