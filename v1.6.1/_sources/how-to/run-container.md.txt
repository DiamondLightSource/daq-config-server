# Run in a container

Pre-built containers with daq-config-server and its dependencies already
installed are available on [Github Container Registry](https://ghcr.io/DiamondLightSource/daq-config-server).

## Starting the container

To pull the container from github container registry and run:

```
$ docker run ghcr.io/diamondlightsource/daq-config-server:latest --version
```

To get a released version, use a numbered release instead of `latest`.
