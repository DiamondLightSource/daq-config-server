# Deploying to production

The production config server is deployed into argus using ArgoCD, you can see this deployment [here](https://argocd.diamond.ac.uk/applications/daq-config-server/daq-config-server). 

To update this:

1. [Create a new release on github](https://github.com/DiamondLightSource/daq-config-server/releases). Ensuring semantic versioning and that the release notes are sensible.

2. Ensure the new [container](https://github.com/orgs/DiamondLightSource/packages/container/package/daq-config-server) and [helm chart](https://github.com/orgs/DiamondLightSource/packages/container/package/charts%2Fdaq-config-server) have been published

3. Clone the [services-repo](https://gitlab.diamond.ac.uk/daq/athena-app/) locally

4. Update the `services/daq-config-server/Chart.yaml` to have the new version numbers. Including changing the chart version as specified in the comment in the file.

5. Update the `Chart.lock` by running:

    ```
    cd services/numtracker
    helm dependency update . 
    ```

    For an example of this and the previous step see [here](https://gitlab.diamond.ac.uk/daq/athena-app/-/merge_requests/34)

6. Merge this as a MR (you will need approval from a DAQ team lead)

6. Ensure the version in [argoCD](https://argocd.diamond.ac.uk/applications/daq-config-server/daq-config-server) updates. This should be automatic and take no longer than 5 mins.
