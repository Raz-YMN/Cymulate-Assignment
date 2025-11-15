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
helm install crypto ./k8s
```

And your chart should now be deploying!

## Port-Forwarding
If running from a local cluster, you can port-forward using a Kubernetes UI like [Lens](https://k8slens.dev/) or using kubectl.

The relevant services and their ports are (assuming installation with release name crypto):\
crypto-bitcoin-price - 8000\
crypto-kube-prometheus-sta-prometheus - 9090\
jaeger-query - 16686\
crypto-grafana - 3000\
crypto-jenkins - 8080

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
Grafana generates a new admin password every time it's deployed. The password can be retrieved using:
linux:
```commandline
kubectl get secret --namespace default crypto-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```
windows (using powershell):
```commandline
powershell -Command "[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String((kubectl get secret --namespace default crypto-grafana -o jsonpath='{.data.admin-password}')))"
```
Jaeger and Prometheus need no authentication and are available through the mentioned ports.

## App Endpoints
`localhost:8000/price` - retrieves the default coin in the default currency (uses env vars values)\
`localhost:8000/price?crypto=bitcoin&currency=usd` - allows for queried specification of coin type and currency\
`localhost:8000/metrics` - displays app metrics
`localhost:8000/health` - displays whether app is healthy
`localhost:8000/docs` - fastapi docs

## Known Limitations
- Jenkins deploys and a Jenkinsfile exists, but due to most of the stages being reliant on ecr/aws and slack, CI/CD won't run.
- Some of prometheus' targets (specifically some of it's own services) requires authentication to access /metrics and thus those targets are down.
- While the app supports change of target endpoint via env variable, most sites probably won't allow a query in the same format as coingecko.