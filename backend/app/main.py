# backend/app/main.py

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from .database import create_db_tables
from .models import ServerInstance

from datetime import datetime

app = FastAPI(
    title="Korniszon",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/api/openapi.json",
)

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

@app.get("/setup/initdb")
async def init_db():
    create_db_tables()