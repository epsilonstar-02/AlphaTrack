import numpy as np
from sklearn.linear_model import LinearRegression
from app.services.stock_service import fetch_stock_data

def predict_next_day(symbol: str, days: int = 30) -> float:
    """
    Predicts the next day's closing price for the given stock symbol.

    Args:
        symbol (str): Stock symbol to predict.
        days (int, optional): Number of recent days to use for prediction. Defaults to 30.

    Returns:
        float: Predicted closing price for the next day.
    """
    stock_data = fetch_stock_data(symbol)
    prices = stock_data.get("data", [])[-days:]

    if not prices or len(prices) < 2:
        raise ValueError("Not enough data to make a prediction.")

    closes = [item["close"] for item in prices]
    X = np.arange(len(closes)).reshape(-1, 1)
    y = np.array(closes)

    model = LinearRegression()
    model.fit(X, y)

    next_day = np.array([[len(closes)]])
    predicted = model.predict(next_day)[0]

    return round(float(predicted), 2)
