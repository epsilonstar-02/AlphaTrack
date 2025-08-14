from fastapi import APIRouter, HTTPException
import json
import os
import re
from app.services.stock_service import fetch_stock_data
from app.services.prediction_service import predict_next_day

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/companies")
async def get_companies():
    try:
        companies_path = os.path.join("data", "companies.json")
        if not os.path.exists(companies_path):
            raise HTTPException(status_code=404, detail="Companies data file not found")
        with open(companies_path, "r", encoding="utf-8") as f:
            companies = json.load(f)
        if not isinstance(companies, dict):
            raise HTTPException(status_code=500, detail="Invalid companies data format")
        companies_list = [
            {"symbol": symbol, "name": name} 
            for symbol, name in companies.items()
            if symbol and name
        ]
        return {"companies": companies_list}
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in companies file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading companies: {str(e)}")

@router.get("/stock/{symbol}")
async def get_stock_data(symbol: str):
    if not symbol or not re.match(r"^[A-Za-z]{1,5}$", symbol.strip()):
        raise HTTPException(status_code=400, detail="Invalid stock symbol format")
    data = fetch_stock_data(symbol)
    if "error" in data:
        raise HTTPException(status_code=500, detail=data["error"])
    return data

@router.get("/stocks")
async def get_stocks():
    try:
        companies_path = os.path.join("data", "companies.json")
        if not os.path.exists(companies_path):
            raise HTTPException(status_code=404, detail="Companies data file not found")
        with open(companies_path, "r", encoding="utf-8") as f:
            companies = json.load(f)
        stocks = [
            {
                "symbol": symbol,
                "name": name,
                "sector": "Unknown",
                "industry": "Unknown"
            }
            for symbol, name in companies.items()
        ]
        return {"stocks": stocks, "count": len(stocks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stocks: {str(e)}")

@router.get("/companies/{symbol}")
async def get_company_by_symbol(symbol: str):
    companies_path = os.path.join("data", "companies.json")
    if not os.path.exists(companies_path):
        raise HTTPException(status_code=404, detail="Companies data file not found")
    with open(companies_path, "r", encoding="utf-8") as f:
        companies = json.load(f)
    name = companies.get(symbol.upper())
    if not name:
        raise HTTPException(status_code=404, detail="Company not found")
    return {
        "symbol": symbol.upper(),
        "name": name,
        "sector": "Unknown",
        "industry": "Unknown",
        "description": "",
        "created_at": None,
        "updated_at": None
    }

 

# Prediction endpoint
@router.get("/predict/{symbol}")
async def predict_stock_next_day(symbol: str, days: int = 30):
    if not symbol or not re.match(r"^[A-Za-z]{1,5}$", symbol.strip()):
        raise HTTPException(status_code=400, detail="Invalid stock symbol format")
    try:
        prediction = predict_next_day(symbol, days)
        return {"symbol": symbol.upper(), "predictedClose": prediction, "days_used": days}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
