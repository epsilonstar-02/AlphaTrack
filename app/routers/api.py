from fastapi import APIRouter, HTTPException
import json
import os
import re
import logging
from pathlib import Path
from app.services.stock_service import fetch_stock_data
from app.services.prediction_service import predict_next_day

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify API is working."""
    return {"status": "ok", "message": "API is working"}

@router.get("/diag/env")
async def diag_env():
    """Diagnostic endpoint: returns whether the API key is available."""
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    has_key = bool(api_key)
    key_length = len(api_key) if api_key else 0
    return {
        "hasApiKey": has_key,
        "keyLength": key_length,
        "keyPreview": api_key[:8] + "..." if api_key and len(api_key) > 8 else None
    }

@router.get("/diag/paths")
async def diag_paths():
    """Diagnostic endpoint: returns path information for debugging."""
    cwd = os.getcwd()
    project_root = str(PROJECT_ROOT)
    data_path = str(PROJECT_ROOT / "data")
    companies_path = str(PROJECT_ROOT / "data" / "companies.json")
    
    return {
        "cwd": cwd,
        "project_root": project_root,
        "data_path": data_path,
        "companies_path": companies_path,
        "project_root_exists": PROJECT_ROOT.exists(),
        "data_path_exists": (PROJECT_ROOT / "data").exists(),
        "companies_file_exists": (PROJECT_ROOT / "data" / "companies.json").exists(),
        "files_in_project_root": list(str(p) for p in PROJECT_ROOT.iterdir()) if PROJECT_ROOT.exists() else [],
        "files_in_data": list(str(p) for p in (PROJECT_ROOT / "data").iterdir()) if (PROJECT_ROOT / "data").exists() else []
    }

@router.get("/companies")
async def get_companies():
    try:
        companies_path = PROJECT_ROOT / "data" / "companies.json"
        logger.info(f"Looking for companies file at: {companies_path}")
        logger.info(f"Companies file exists: {companies_path.exists()}")
        logger.info(f"Project root exists: {PROJECT_ROOT.exists()}")
        logger.info(f"Data directory exists: {(PROJECT_ROOT / 'data').exists()}")
        
        if not companies_path.exists():
            logger.error(f"Companies data file not found at {companies_path}")
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
        logger.info(f"Successfully loaded {len(companies_list)} companies")
        return {"companies": companies_list}
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        raise HTTPException(status_code=500, detail=f"Invalid JSON in companies file: {str(e)}")
    except Exception as e:
        logger.error(f"Error loading companies: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error loading companies: {str(e)}")

@router.get("/stock/{symbol}")
async def get_stock_data(symbol: str):
    logger.info(f"Fetching stock data for symbol: {symbol}")
    if not symbol or not re.match(r"^[A-Za-z]{1,5}$", symbol.strip()):
        logger.warning(f"Invalid stock symbol format: {symbol}")
        raise HTTPException(status_code=400, detail="Invalid stock symbol format")
    
    try:
        data = fetch_stock_data(symbol)
        if "error" in data:
            status = data.get("status", 500)
            err = data.get("error")
            if isinstance(err, dict):
                msg = err.get("message") or err.get("code") or str(err)
            else:
                msg = str(err)
            logger.error(f"Stock service error for {symbol}: {msg}")
            raise HTTPException(status_code=status, detail=msg)
        
        logger.info(f"Successfully fetched stock data for {symbol}")
        return data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching stock data for {symbol}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/stocks")
async def get_stocks():
    try:
        companies_path = PROJECT_ROOT / "data" / "companies.json"
        if not companies_path.exists():
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
    companies_path = PROJECT_ROOT / "data" / "companies.json"
    if not companies_path.exists():
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
