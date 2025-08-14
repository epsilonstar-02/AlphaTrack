from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from pathlib import Path
from app.routers import ui, api

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")
    logger.info(f"Project root: {PROJECT_ROOT}")
    logger.info(f"Static files directory: {PROJECT_ROOT / 'app' / 'static'}")
    logger.info(f"Templates directory: {PROJECT_ROOT / 'app' / 'templates'}")
    logger.info(f"Data directory: {PROJECT_ROOT / 'data'}")
    
    # Check if critical files exist
    static_dir = PROJECT_ROOT / "app" / "static"
    templates_dir = PROJECT_ROOT / "app" / "templates"
    data_dir = PROJECT_ROOT / "data"
    companies_file = data_dir / "companies.json"
    
    logger.info(f"Static directory exists: {static_dir.exists()}")
    logger.info(f"Templates directory exists: {templates_dir.exists()}")
    logger.info(f"Data directory exists: {data_dir.exists()}")
    logger.info(f"Companies file exists: {companies_file.exists()}")
    
    if companies_file.exists():
        try:
            import json
            with open(companies_file) as f:
                companies_data = json.load(f)
            logger.info(f"Companies file loaded successfully with {len(companies_data)} companies")
        except Exception as e:
            logger.error(f"Error reading companies file: {e}")
    
    yield
    logger.info("Shutting down application...")

app = FastAPI(
    title="Stock Market Dashboard", 
    description="A corporate-style stock market dashboard with real-time data",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception for {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "path": str(request.url.path)}
    )

try:
    static_path = PROJECT_ROOT / "app" / "static"
    logger.info(f"Mounting static files from: {static_path}")
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
except Exception as e:
    logger.error(f"Failed to mount static files: {e}")
    raise

app.include_router(ui.router)
app.include_router(api.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
