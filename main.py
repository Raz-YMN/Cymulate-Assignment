from fastapi import FastAPI, Query
import requests
import os

app = FastAPI()

supported_currencies = ["usd", "ils"]

CURRENCY = os.getenv("CURRENCY", "usd").lower()
if CURRENCY not in supported_currencies:
    print("Non-supported currency, defaulting to USD") # TODO: Change to log
    CURRENCY = "usd"

BASE_URL = os.getenv("BASE_URL", f"https://api.coingecko.com/api/v3/simple/price")

@app.get("/price")
def get_crypto_price(crypto: str = Query("bitcoin", description="Cryptocurrency name"),
                     currency: str = Query("usd", description="Currency type")):
    params = {
    "ids": crypto,
    "vs_currencies": currency
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()

    if crypto not in data:
        return {"error": f"Price not found for '{crypto}'"}

    return {"crypto": crypto, "price": data[crypto][currency.lower()]}

print(get_crypto_price("bitcoin", "usd"))