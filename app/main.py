from fastapi import FastAPI
from app.routers import ui, api

app = FastAPI()

app.include_router(ui.router)
app.include_router(api.router)
