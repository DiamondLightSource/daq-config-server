# Current and future features


## Current features
- Provide an endpoint to read any whitelisted file on diamond's shared filesystem, with static typing support.
- Periodically check the main branch's to update the whitelist.
- Provide a client module for users to easily communicate with the server, with caching.
- Have this service hosted on diamond's central argus cluster - with url `https://daq-config-server.diamond.ac.uk`


## Future features
Note that this is not actively ongoing work, but features that we are aware will be needed in the future.
- Provide server-side formatting for commonly used configuration files - eg `beamline_parameters.txt` should be returned as a dictionary.
- Remove absolute filepath as a user dependancy. For example, once we have a good picture of which files are being read, the client should be able to request the beamline parameters with something like `client.get_file_contents(SUPPORTED_CONFIG_FILES.BeamlineParameters, beamline=i03)`
- Add authorisation + authentication. This is a pre-requisite for file-writing.
- Add endpoints for configuration file-writing. At this point, we can begin to remove any configuration from the filesystem. The config-server will use a redis database to store these values, and we can have a simple web-interface to change the values.
