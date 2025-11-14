import logging

from fastapi import FastAPI, Query, Response
import requests
import os

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from logger import init_logger
from metrics import *

init_logger()
logger = logging.getLogger()

app = FastAPI()

supported_currencies = ["usd", "ils"]
supported_coins = ["bitcoin"]

CURRENCY = os.getenv("API_CURRENCY", "usd").lower()
if CURRENCY not in supported_currencies:
    logger.warning("Non-supported currency, defaulting to USD")
    CURRENCY = "usd"

COIN_TYPE = os.getenv("API_COIN_TYPE", "bitcoin").lower()
if COIN_TYPE not in supported_coins:
    logger.warning("Non-supported coin, defaulting to bitcoin")
    COIN_TYPE = "bitcoin"

BASE_URL = os.getenv("API_URL", f"https://api.coingecko.com/api/v3/simple/price")

@app.get("/price")
def get_crypto_price(crypto: str = Query(COIN_TYPE, description="Cryptocurrency name"),
                     currency: str = Query(CURRENCY, description="Currency type")):
    params = {
    "ids": crypto,
    "vs_currencies": currency
    }
    start = time.time()
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch price: {e}")
        increase_site_api_error(BASE_URL)
        return {"error": "Failed to fetch price"}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        increase_site_api_error(BASE_URL)
        return {"error": "Unexpected error"}

    if crypto not in data:
        increase_no_price(BASE_URL)
        record_latency(BASE_URL, COIN_TYPE, start)
        logger.error(f"Price not found for '{crypto}'")
        return {"error": f"Price not found for '{crypto}'"}

    increase_request_count(BASE_URL, crypto)
    record_latency(BASE_URL, COIN_TYPE, start)
    logger.info(f"Successfully fetched price for {crypto} from {BASE_URL}")
    return {"crypto": crypto, "price": data[crypto][currency.lower()]}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)