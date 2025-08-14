# Jarnox — Stock Market Dashboard

FastAPI-powered dashboard that visualizes real-time stock market data and adds a simple next-day price prediction. It serves a corporate-style UI (Bootstrap + Plotly) and a clean REST API.

## Features

- Modern UI with sidebar company picker and interactive Plotly charts
- Real-time stock data via Alpha Vantage API (with 5-minute in-memory caching)
- Summary stats: latest close, 52-week high/low, average volume
- Simple ML prediction (Linear Regression) for next-day close
- Fully containerized with Docker; health check and ready for Compose

## Tech Stack

- Backend: FastAPI, Uvicorn
- Templates/UI: Jinja2, Bootstrap 5, Plotly.js
- Data & HTTP: requests, python-dotenv
- ML: scikit-learn, NumPy, pandas

## Project Structure

```
app/
	main.py                 # FastAPI app entry
	routers/
		ui.py                 # HTML UI routes
		api.py                # REST API routes
	services/
		stock_service.py      # Alpha Vantage fetch + processing + caching
		prediction_service.py # Linear regression prediction
	templates/              # Jinja2 templates (Bootstrap + components)
	static/                 # CSS/JS assets (Plotly chart + UI interactions)
data/
	companies.json          # Symbol-to-name map used by UI (loaded by /api/companies)
Dockerfile
docker-compose.yml
requirements.txt
pyproject.toml
```

## Prerequisites

- Python 3.12+
- Alpha Vantage API key (free) — set it in an `.env` file
- Optional: Docker and Docker Compose

Create a `.env` file at the repo root with:

```
ALPHAVANTAGE_API_KEY=your_key_here
```

## Run locally (Python)

Using Windows PowerShell:

```powershell
# 1) Create & activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3) Create .env with your Alpha Vantage key (see above)

# 4) Start the server (auto-reload for dev)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Visit:

- UI: http://127.0.0.1:8000/
- API docs (Swagger): http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

## Run with Docker

1) Ensure `.env` exists with `ALPHAVANTAGE_API_KEY`

```powershell
docker compose up --build -d
```

Then open http://127.0.0.1:8000

Notes:

- The `data/` folder is mounted read-only into the container.
- Container exposes port 8000 and includes a health check hitting `/health`.

## API Endpoints

- GET `/` — HTML dashboard (Jinja2 template)
- GET `/health` — Service health status
- GET `/api/companies` — List companies from `data/companies.json`
- GET `/api/stock/{symbol}` — Processed historical OHLCV for a symbol (last ~100 days)
- GET `/api/stocks` — Convenience list of stocks derived from companies
- GET `/api/companies/{symbol}` — Company metadata by symbol
- GET `/api/predict/{symbol}?days=30` — Next-day close prediction using last N days

Swagger UI and JSON schemas are available at `/docs`.

## How it works

- Data fetch: `stock_service.fetch_stock_data` calls Alpha Vantage `TIME_SERIES_DAILY` and caches responses for 5 minutes.
- Processing: Converts raw time series into an array of data points and aggregates (latestClose, 52W high/low, averageVolume).
- Prediction: `prediction_service.predict_next_day` fits a simple `LinearRegression` over recent closes and predicts the next index point.

## Development Notes

- UI scripts live in `app/static/js/`:
	- `ui_interactions.js` wires the sidebar, stats cards, and prediction fetch
	- `chart.js` renders Plotly charts (line, candlestick, volume)
- Templates in `app/templates/` use Bootstrap 5 and components under `templates/components/`.
- CORS is enabled for all origins by default (adjust in `app/main.py` if needed).

## Troubleshooting

- 429 or empty data: Alpha Vantage has strict rate limits; consider retrying after a minute.
- Missing key: If `ALPHAVANTAGE_API_KEY` isn’t set, `/api/stock/{symbol}` returns an error payload.
- No companies: Ensure `data/companies.json` exists and is valid JSON.

## License

MIT — see `LICENSE`.

## Disclaimer

This project is for educational/demo purposes. It’s not financial advice. Predictions are simplistic and not suitable for trading decisions.

