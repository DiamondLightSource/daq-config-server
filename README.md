[![CI](https://github.com/dperl-dls/config-service/actions/workflows/ci.yml/badge.svg)](https://github.com/dperl-dls/config-service/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/dperl-dls/config-service/branch/main/graph/badge.svg)](https://codecov.io/gh/dperl-dls/config-service)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# config_service

A service to put and get your config values from.

|  Source  |     <https://github.com/dperl-dls/config-service>      |
| :------: | :----------------------------------------------------: |
|  Docker  |  `docker run ghcr.io/dperl-dls/config-service:latest`  |
| Releases | <https://github.com/dperl-dls/config-service/releases> |

A simple app for storing and fetching values. Has a Valkey (Redis) instance as well as options for file-backed legacy
values (e.g. `beamlineParameters`...)

To use the config values in an experimental application (e.g. Hyperion) you can do:

```python
from config_service.client import ConfigService

config_service = ConfigService("<service ip address>", <port>)

use_stub_offsets: bool = config_service.best_effort_get_feature_flag("use_stub_offsets")

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
development.

To deploy a live version, you can run the above script with no arguments and then while logged in to
argus, run `kubectl rollout restart deployment`

To test locally, you can build everything with `./deployment/build_and_push_all.sh --dev --no-push` and then
run the containers `daq-config-server-dev` (with the command `config-service --dev`), `daq-config-server-db-dev`,
and `daq-config-server-gui-dev`, all with the `--net host` option.
