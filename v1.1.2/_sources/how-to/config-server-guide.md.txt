# Guide to using the config-server

The server is centrally hosted on argus and is accessible anywhere within the Diamond network. You can quickly get a feel for it using FastAPI's generated Swagger UI at https://daq-config.diamond.ac.uk/docs


This library provides a python client to easily make requests from Bluesky code. The client can use caching to prevent needlessly making time-consuming requests on data which won't have changed. You can choose the maximum number of items it can hold as well as the lifetime of an item upon instantiation.

```python
from daq_config_server.client import ConfigServer

config_server = ConfigServer("https://daq-config.diamond.ac.uk", cache_size = 10, cache_lifetime_s = 3600)
```

You can then make a request through this client through its `get_file_contents` function. If you are reading a file which may have changed since the client last read it, you should set the appropriate flag to reset the cache for that result - this forces a new request and stores that new result in the cache.
```python
config_server.get_file_contents(FILE_PATH,reset_cached_result=True)
```
By default, this will return the file's raw string output - which includes things like linebreaks. It is up to you to format this output - using `splitlines()` will get you a list where each item is a line in the file. `get_file_contents` has a `desired_return_type` parameter where you can instead ask for a `dict`, `bytes` or a one of the `pydantic models` defined in the server. The server will try and do the conversion, and respond with an HTTP error if the requested file is incompatible with that type, or a pydantic validation error if the data cannot be converted to the pydantic model provided. Custom [file converters](#file-converters) can be used to specify how a file should be converted to a dict or pydantic model.

(file-converters)=
# File converters

Converters can be used to turn a file into a standard format server-side, reducing the complexity of reading config files client-side. Converters can convert config files to a `dict` or pydantic model, and the same pydantic model can be reconstructed client-side by the `get_file_contents` method. Available converters and models exist [here](https://github.com/DiamondLightSource/daq-config-server/blob/main/src/daq_config_server/models/converters/), divided into modules based on the type of config they convert - see if there's a suitable converter you can use before adding your own. [This dictionary](https://github.com/DiamondLightSource/daq-config-server/blob/main/src/daq_config_server/models/converters/_file_converter_map.py) maps files to converters. Add the path of your config file and a suitable converter to this dictionary and it will automatically be used by the config server when a request for that file is made. Models should be added to this [`__init__.py`](https://github.com/DiamondLightSource/daq-config-server/blob/main/src/daq_config_server/models/__init__.py) so that they can be imported with `from daq_config_server.models import MyModel`.

A request for `str` or `bytes` will fetch the raw file with no conversion.

# Adding files to the whitelist

For [security reasons](../explanations/whitelist_info.md), only files existing on the [whitelist](https://github.com/DiamondLightSource/daq-config-server/blob/main/whitelist.yaml) can be read. Please make a PR to add a file to the whitelist. If unsure, please ask in the #daq-config-server slack channel or create a GitHub issue. To make the config-server as quick to use as possible, the server will check any requests against the `whitelist.yaml` file on **the main branch of the repository**, rather than the whitelist in the latest release. The server will check for updates every 5 minutes.

# Reading sensitive information

If you need to read a file which contains sensitive information, or `dls-dasc` doesn't have the permissions to read your file, you should encrypt this file as a [sealed secret](https://github.com/bitnami-labs/sealed-secrets) on your beamline cluster, and mount this in your BlueAPI service.
