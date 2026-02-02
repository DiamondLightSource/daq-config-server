# Deploying to production

The production config server is deployed into argus using ArgoCD, you can see this deployment [here](https://argocd.diamond.ac.uk/applications/daq-config-server/daq-config-server). 

To update this:

1. [Create a new release on github](https://github.com/DiamondLightSource/daq-config-server/releases). Ensuring semantic versioning and that the release notes are sensible.

2. Ensure the new [container](https://github.com/orgs/DiamondLightSource/packages/container/package/daq-config-server) and [helm chart](https://github.com/orgs/DiamondLightSource/packages/container/package/charts%2Fdaq-config-server) have been published

3. Clone the [services-repo](https://gitlab.diamond.ac.uk/daq/athena-app/) locally

4. Update the `services/daq-config-server/Chart.yaml` to have the new version numbers. Including changing the chart version as specified in the comment in the file.

5. Update the `Chart.lock` by running:

    ```
    cd services/daq-config-server/
    module load helm
    helm dependency update . 
    ```

    For an example of this and the previous step see [here](https://gitlab.diamond.ac.uk/daq/athena-app/-/merge_requests/34)

6. Merge this as a MR (you will need approval from a DAQ team lead)

7. Ensure the version in [argoCD](https://argocd.diamond.ac.uk/applications/daq-config-server/daq-config-server) updates. This should be automatic and take no longer than 5 mins.


# Deploying to a beamline cluster

The config server can also be deployed to beamline clusters.

To do this:

1. Request a new ingress from the cloud team from [this page](https://jira.diamond.ac.uk/servicedesk/customer/portal/2/create/156). For example, for i03 the request would be
- Namespace Name: `i03-beamline`
- Ingress Names: `i03-daq-config.diamond.ac.uk`

2. In the {beamline}-services repo on gitlab, create a new folder inside the services folder called `{beamline}-daq-config-server/`. Create a `Chart.yaml` and `values.yaml` here. See [here](https://gitlab.diamond.ac.uk/controls/containers/beamline/i03-services/-/tree/main/services/i03-daq-config-server?ref_type=heads) for an example in `i03-services`. Make sure the ingress section in `values.yaml` matches the ingress information you requested in step 1.

3. Ensure the `securityContext` section is correct for your beamline. Running `id k8s-ixx-beamline` in a terminal will give you the correct user ID and group ID for your beamline.

4. In the {beamline}-deployment repo on gitlab, update `apps/values.yaml` to include the new config server app by adding the service name below the other services.

5. Check the app is running on [ArgoCD](https://argocd.diamond.ac.uk/applications). If you don't have access to the namespace of the beamline cluster you are deploying to, someone already with access can request to add you [here](https://jira.diamond.ac.uk/servicedesk/customer/portal/2/create/92).

6. Once ArgoCD is showing the app is up and running, check you can retrieve config from the server by visiting the ingress url in a browser with `/docs` to see the interactive API. You should be able to use the `Get Configuration` form to retrieve a config file. For example, here's the [i03 site](https://i03-daq-config.diamond.ac.uk/docs).
