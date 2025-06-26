# Whitelist Security

The centrally-hosted config server is running with the same permissions as the `dls-dasc` group. Since this service currently doesn't have authentication and has `/dls_sw` mounted, we have introduced a whitelist to ensure that nothing sensitve gets read. Most importantly, **nothing confidential should be added to the whitelist**. This includes any experimental data and files containing credentials.

This service was designed primarily to read beamline configuration files, like lookup tables and key-value variables. However, as long the file is safe for **anyone** to read, it can be safely added to the whitelist.

See the [general guide](../how-to/config-server-guide.md) if you need to read sensitive information in your Bluesky plans.
