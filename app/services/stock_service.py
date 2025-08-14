import os
import time
import logging
from typing import Dict, Any

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

stock_cache = {}
CACHE_EXPIRY_SECONDS = 300

def is_cache_valid(timestamp: float) -> bool:
    return time.time() - timestamp < CACHE_EXPIRY_SECONDS

def fetch_stock_data(symbol: str) -> Dict[str, Any]:
    symbol = symbol.upper().strip()
    cache_key = symbol
    if cache_key in stock_cache:
        cached_data, timestamp = stock_cache[cache_key]
        if is_cache_valid(timestamp):
            return cached_data
    try:
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        if not api_key:
            return {
                "error": {"code": "NO_API_KEY", "message": "Alpha Vantage API key not configured"},
                "status": 503,
                "symbol": symbol,
            }
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": api_key,
            "datatype": "json"
        }
        # Simple retry for transient issues
        last_exc = None
        for attempt in range(3):
            try:
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                last_exc = e
                # Do not retry client errors
                if hasattr(e, 'response') and e.response is not None and 400 <= e.response.status_code < 500:
                    raise
                time.sleep(0.5 * (attempt + 1))
        else:
            raise last_exc
        try:
            raw_data = response.json()
        except ValueError as e:
            return {
                "error": {"code": "INVALID_JSON", "message": f"Invalid JSON response: {str(e)}"},
                "status": 502,
                "symbol": symbol,
            }

        # Alpha Vantage often returns Note or Error Message when rate-limited or symbol invalid
        if isinstance(raw_data, dict):
            if "Note" in raw_data:
                return {
                    "error": {"code": "RATE_LIMIT", "message": raw_data.get("Note", "API rate limit reached")},
                    "status": 429,
                    "symbol": symbol,
                }
            if "Error Message" in raw_data:
                return {
                    "error": {"code": "INVALID_SYMBOL", "message": raw_data.get("Error Message", "Invalid symbol")},
                    "status": 404,
                    "symbol": symbol,
                }
            if "Information" in raw_data:
                return {
                    "error": {"code": "SERVICE_INFO", "message": raw_data.get("Information", "Service information/limitation")},
                    "status": 503,
                    "symbol": symbol,
                }

        time_series = raw_data.get("Time Series (Daily)")
        if not isinstance(time_series, dict):
            logger.warning("Upstream response missing time series for %s: keys=%s", symbol, list(raw_data.keys()) if isinstance(raw_data, dict) else type(raw_data))
            return {
                "error": {"code": "DATA_UNAVAILABLE", "message": "Upstream response missing daily time series"},
                "status": 502,
                "symbol": symbol,
            }
        processed_data = process_stock_data(symbol, time_series)
        stock_cache[cache_key] = (processed_data, time.time())
        return processed_data
    except KeyError as e:
        logger.exception("KeyError while processing data for %s", symbol)
        return {
            "error": {"code": "MISSING_FIELD", "message": f"Data field missing: {str(e)}"},
            "status": 502,
            "symbol": symbol,
        }
    except requests.exceptions.RequestException as e:
        logger.exception("Network error while fetching %s", symbol)
        return {
            "error": {"code": "NETWORK_ERROR", "message": f"Network error: {str(e)}"},
            "status": 503,
            "symbol": symbol,
        }
    except Exception as e:
        logger.exception("Unexpected error while fetching %s", symbol)
        return {
            "error": {"code": "UNEXPECTED_ERROR", "message": f"Unexpected error: {str(e)}"},
            "status": 500,
            "symbol": symbol,
        }

def process_stock_data(symbol: str, time_series: Dict[str, Any]) -> Dict[str, Any]:
    data_points = []
    closing_prices = []
    high_prices = []
    low_prices = []
    volumes = []
    sorted_dates = sorted(time_series.keys(), reverse=True)
    limited_dates = sorted_dates[:100]
    try:
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
    except Exception as e:
        logger.exception("Failed to process time series for %s", symbol)
        raise KeyError(str(e))
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
