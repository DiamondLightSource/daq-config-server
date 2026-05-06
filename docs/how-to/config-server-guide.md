# Guide to using the config-server

The server is centrally hosted on argus and is accessible anywhere within the Diamond network. You can quickly get a feel for it using FastAPI's generated [Swagger UI](https://daq-config.diamond.ac.uk/docs).


This library provides a python client to easily make requests from Bluesky code. The client can use caching to prevent needlessly making time-consuming requests on data which won't have changed. You can choose the maximum number of items it can hold as well as the lifetime of an item upon instantiation.

```python
from daq_config_server import ConfigClient

config_client = ConfigClient("https://daq-config.diamond.ac.uk", cache_size = 10, cache_lifetime_s = 3600)
```

You can then make a request through this client through its `get_file_contents` function. If you are reading a file which may have changed since the client last read it, you should set the appropriate flag to reset the cache for that result - this forces a new request and stores that new result in the cache.
```python
config_client.get_file_contents(FILE_PATH,reset_cached_result=True)
```
By default, this will return the file's raw string output - which includes things like linebreaks. It is up to you to format this output - using `splitlines()` will get you a list where each item is a line in the file. `get_file_contents` has a `desired_return_type` parameter where you can instead ask for a `dict`, `bytes` or a one of the `pydantic models` defined in the server. The server will try and do the conversion, and respond with an HTTP error if the requested file is incompatible with that type, or a pydantic validation error if the data cannot be converted to the pydantic model provided. Custom [file converters](#file-converters) can be used to specify how a file should be converted to a dict or pydantic model.

# Converter map configuration

Converters can be used to turn a file into a standard format server-side, reducing the complexity of reading config files client-side. Converters can convert config files to a `dict` or pydantic model, and the same pydantic model can be reconstructed client-side by the `get_file_contents` method. 

The converter map configuration file can be changed by specifying in the AppConfig.yaml:

```yaml
converter_map:
  config_file: /path/to/my/converter_map.yaml
```

The converter_map.yaml configuration file consists of a sequence of alternating `path`, `converter` key-value pairs:

```yaml
- path: "/dls_sw/i23/software/aithre/aithre_display.configuration"
  converter: DisplayConfig
- path: "/dls_sw/i03/software/gda_versions/var/display.configuration"
  converter: DisplayConfig
```

The list of valid converter names can be found in `CONVERTER_FUNCS` in [_file_converter_map.py](https://github.com/DiamondLightSource/daq-config-server/blob/main/src/daq_config_server/app/_file_converter_map.py)

(file-converters)=
# File converters

Available converters and models exist [here](https://github.com/DiamondLightSource/daq-config-server/blob/main/src/daq_config_server/models/), divided into modules based on the type of config they convert - see if there's a suitable converter you can use before adding your own. Add your converter function to the `CONVERTER_FUNCS` dictionary and it will be available for use in the `converter_map.yaml` configuration file. Models should be added to this [`__init__.py`](https://github.com/DiamondLightSource/daq-config-server/blob/main/src/daq_config_server/models/__init__.py) so that they can be imported with `from daq_config_server.models import MyModel`.

A request for `str` or `bytes` will fetch the raw file with no conversion.

# Whitelisting files

For [security reasons](../explanations/whitelist_info.md), only files existing on the [whitelist](https://github.com/DiamondLightSource/daq-config-server/blob/main/whitelist.yaml) can be read. Older versions of the daq-config-server periodically polled the main branch of this repository to fetch updates to their whitelist. However, file-based configuration is now preferred and this shared whitelist is now deprecated. Beamlines using such older releases of the config server should when they next upgrade their daq-config-server to a newer release add their beamline-specific whitelist configuration to their beamline configmap and submit a PR to this project to remove their entries from the legacy whitelist after deploying their updated server.

Similarly, beamlines that decide to migrate from the shared config server to a beamline-specific deployment should also inform the daq-config-server maintainers and submit a PR to remove their whitelist entries from the site-wide configuration. 

# File-based whitelist

The whitelist is configured using a yaml file, by default the location is ``/etc/config/whitelist.yaml``. The location of the whitelist is configurable in the AppConfig YAML, for example:

```yaml
whitelist:
  config_file: "/path/to/my/whitelist.yaml"
```

# Reading sensitive information

If you need to read a file which contains sensitive information, or `dls-dasc` doesn't have the permissions to read your file, you should encrypt this file as a [sealed secret](https://github.com/bitnami-labs/sealed-secrets) on your beamline cluster, and mount this in your BlueAPI service.
