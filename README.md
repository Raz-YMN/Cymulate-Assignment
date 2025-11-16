# Cymulate-Assignment

## What's here?
This repository contains the code for a fastapi app which allows you to query sites for prices of different crypto coins in different currencies, as well as a chart
for deploying the application on your cluster of choice.

The chart also contains Prometheus for sampling metrics from your application as well as your cluster, Jaeger and OpenTelemetry Collector for sampling traces,
and Grafana to display those in pre-installed dashboards.

If deploying on AWS, Karpenter can be enabled in the `Values.yaml` file to allow for node management and cost reduction.

The chart also deploys Jenkins to use with the pre-existing Jenkinsfile.

## How to install

### Stand-Alone crypto price fetching app
If you want to deploy the application locally without a cluster and without all the other services, simply install [Docker](https://www.docker.com/) and run the following from within the
repositories root:

```commandline
docker build -t Crypto .
docker run -p 8000:8000 crypto-price
```

You should then see your app running on localhost:8000/price

**IMPORTANT**:

Since this app is meant to be run with the whole stack defined in the chart, you may be seeing errors regarding traces. You can safely ignore those since they won't affect the usage of the app.

### On cluster
You may deploy the app on an existing cluster, or locally using services like [kind](https://kind.sigs.k8s.io/) or [minikube](https://minikube.sigs.k8s.io/)

kind:
```commandline
kind create cluster --name mycluster
```
minikube:
```commandline
minikube start --profile mycluster
```

Make sure you have [kubectl](https://kubernetes.io/docs/tasks/tools/) installed, and then run:
```commandline
kubectl config get-contexts
kubectl config use-context mycontext
```

To install the chart using [helm](https://helm.sh/docs/intro/install/) run from the root of the repository:
```commandline
helm dep up
helm install crypto ./k8s/Crypto
```

And your chart should now be deploying!

## Port-Forwarding
If running from a local cluster, you can port-forward using a Kubernetes UI like [Lens](https://k8slens.dev/) or using kubectl.

The relevant services and their ports are (assuming installation with release name crypto):\
`crypto-bitcoin-price - 8000`\
`crypto-kube-prometheus-sta-prometheus - 9090`\
`jaeger-query - 16686`\
`crypto-grafana - 3000`\
`crypto-jenkins - 8080`

## Environment Variables
There are no required environment variables. Not setting any will use the default values in the chart's `values.yaml`.\
That being said, these are the values you can change:
```yaml
env:
  - name: API_CURRENCY # What type of currency to show the price in
    value: usd
  - name: API_COIN_TYPE # Which coin to query for
    value: bitcoin
  - name: BASE_URL # Backend to query for coin prices
    value: https://api.coingecko.com/api/v3/simple/price
  - name: OPENTELEMETRY_HOST # Opentelemetry host to which the app will send traces
    value: http://opentelemetry-collector.default.svc.cluster.local
  - name: OPENTELEMETRY_PORT # Port for opentelemetry host
    value: "4318"
```

## Authentication
Grafana and Jenkins generate a new admin password every time they're deployed. Username is `admin` and the password can be retrieved using:\
linux:
```commandline
kubectl get secret --namespace default crypto-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```
windows (using powershell):
```commandline
powershell -Command "[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String((kubectl get secret --namespace default crypto-grafana -o jsonpath='{.data.admin-password}')))"
```
Swap `crypto-grafana` with `crypto-jenkins` and `data.admin-password` with `data.jenkins-admin-password` for Jenkins\
Jaeger and Prometheus need no authentication and are available through the mentioned ports.

## Istio Usage
To install and use Istio's service mesh first install the main crypto app and then cd into `./k8s/Istio` and run:
```commandline
help dep up
helm install istio . -n istio-system --create-namespace
```

**KNOWN BUG**\
since the ingress gateway deployment deploys at the same time as istiod, istiod doesn't change the gateway's image in time from
`auto` to the correct one. This means you may have to delete the gateway deployment and run:
```commandline
helm upgrade istio . -n istio-system
```

After installing, your crypto pod will now have istio's proxy sidecar, and you can access the api through the istio gateway by using it's `80` port.\
You can do so via Lens or by running:
```commandline
kubectl port-forward svc/istio-ingressgateway 8000:80 --namespace istio-system
```

## App Endpoints
`localhost:8000/price` - retrieves the default coin in the default currency (uses env vars values)\
`localhost:8000/price?crypto=bitcoin&currency=usd` - allows for queried specification of coin type and currency\
`localhost:8000/metrics` - displays app metrics
`localhost:8000/health` - displays whether app is healthy
`localhost:8000/docs` - fastapi docs

## Service Logs
`2025-11-15 21:44:15,973 - INFO - Sending telemetry to http://opentelemetry-collector.default.svc.cluster.local:4318/v1/traces
2025-11-15 21:44:16,012 - INFO - Started server process [1]
2025-11-15 21:44:16,013 - INFO - Waiting for application startup.
2025-11-15 21:44:16,013 - INFO - Application startup complete.
2025-11-15 21:44:16,015 - INFO - Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
2025-11-15 21:45:13,566 - ERROR - Price not found for 'asdasdsa'
2025-11-15 21:45:14,030 - ERROR - Price not found for 'asdasdsa'
2025-11-15 21:45:17,714 - INFO - Successfully fetched price for bitcoin from https://api.coingecko.com/api/v3/simple/price
2025-11-15 21:48:09,568 - INFO - Successfully fetched price for ethereum from https://api.coingecko.com/api/v3/simple/price
2025-11-15 21:49:29,762 - INFO - Successfully fetched price for ethereum from https://api.coingecko.com/api/v3/simple/price
2025-11-15 21:49:30,292 - ERROR - Failed to fetch price: 429 Client Error: Too Many Requests for url: https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=ils
2025-11-15 21:49:31,210 - ERROR - Failed to fetch price: 429 Client Error: Too Many Requests for url: https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=ils` \
Errors come from rate limiting on endpoint

## Known Limitations
- Jenkins deploys and a Jenkinsfile exists, but due to most of the stages being reliant on ecr/aws and slack, CI/CD won't run.
- Some of prometheus' targets (specifically some of it's own services) requires certificates to access /metrics and thus those targets are down.
- While the app supports change of target endpoint via env variable, most sites probably won't allow a query in the same format as coingecko.
- Jaeger datasource for the tracing dashboard needs to be created manually due to time constraints