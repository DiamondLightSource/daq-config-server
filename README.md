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

config_service = ConfigService("<service ip address>", 8555)

use_stub_offsets: bool = config_service.best_effort_get_feature_flag("use_stub_offsets")

```

To work with the GUI you will probably need to run:

```bash
module load node
npm install
```

