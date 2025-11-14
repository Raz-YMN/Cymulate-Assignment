from prometheus_client import Counter, Histogram
import time

successful_requests_count = Counter(
    "crypto_price_successful_requests_total",
    "Total number of successful requests to /price for a specific coin",
    ["endpoint", "coin_type"]
)

price_error_count = Counter(
    "crypto_price_not_found_error_total",
    "Total number of fails regarding finding price of coin",
    ["endpoint"]
)

target_site_api_error_count = Counter(
    "endpoint_api_error_total",
    "Total number of errors trying to request data from target site",
    ["endpoint"]
)

target_site_request_latency = Histogram(
    "endpoint_api_request_latency_seconds",
    "Latency of requests to /price endpoint",
    ["endpoint", "coin_type"]
)

def increase_successful_request_count(endpoint: str, coin_type: str):
    successful_requests_count.labels(endpoint=endpoint, coin_type=coin_type).inc()

def increase_no_price(endpoint: str):
    price_error_count.labels(endpoint=endpoint).inc()

def increase_site_api_error(endpoint: str):
    target_site_api_error_count.labels(endpoint=endpoint).inc()

def record_latency(endpoint: str, coin_type: str, start):
    target_site_request_latency.labels(endpoint=endpoint, coin_type=coin_type).observe(time.time() - start)