import os
import time
from typing import Dict

import requests
from dotenv import load_dotenv

load_dotenv()

stock_cache = {}
CACHE_EXPIRY_SECONDS = 300

def is_cache_valid(timestamp: float) -> bool:
    return time.time() - timestamp < CACHE_EXPIRY_SECONDS

def fetch_stock_data(symbol: str) -> Dict:
    symbol = symbol.upper().strip()
    cache_key = symbol
    if cache_key in stock_cache:
        cached_data, timestamp = stock_cache[cache_key]
        if is_cache_valid(timestamp):
            return cached_data
    try:
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        if not api_key:
            return {"error": "Alpha Vantage API key not configured", "symbol": symbol}
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": api_key,
            "datatype": "json"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        try:
            raw_data = response.json()
        except ValueError as e:
            return {"error": f"Invalid JSON response: {str(e)}", "symbol": symbol}
        time_series = raw_data["Time Series (Daily)"]
        processed_data = process_stock_data(symbol, time_series)
        stock_cache[cache_key] = (processed_data, time.time())
        return processed_data
    except KeyError as e:
        return {"error": f"Data field missing: {str(e)}", "symbol": symbol}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}", "symbol": symbol}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}", "symbol": symbol}

def process_stock_data(symbol: str, time_series: Dict) -> Dict:
    data_points = []
    closing_prices = []
    high_prices = []
    low_prices = []
    volumes = []
    sorted_dates = sorted(time_series.keys(), reverse=True)
    limited_dates = sorted_dates[:100]
    for date in reversed(limited_dates):
        daily_data = time_series[date]
        data_point = {
            "date": date,
            "open": float(daily_data["1. open"]),
            "high": float(daily_data["2. high"]),
            "low": float(daily_data["3. low"]),
            "close": float(daily_data["4. close"]),
            "volume": int(float(daily_data["5. volume"]))
        }
        data_points.append(data_point)
        closing_prices.append(data_point["close"])
        high_prices.append(data_point["high"])
        low_prices.append(data_point["low"])
        volumes.append(data_point["volume"])
    latest_close = closing_prices[-1] if closing_prices else 0
    fifty_two_week_high = max(high_prices) if high_prices else 0
    fifty_two_week_low = min(low_prices) if low_prices else 0
    average_volume = sum(volumes) / len(volumes) if volumes and len(volumes) > 0 else 0
    return {
        "symbol": symbol,
        "data": data_points,
        "latestClose": round(latest_close, 2),
        "fiftyTwoWeekHigh": round(fifty_two_week_high, 2),
        "fiftyTwoWeekLow": round(fifty_two_week_low, 2),
        "averageVolume": round(average_volume, 0)
    }
