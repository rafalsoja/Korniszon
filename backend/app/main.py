# backend/app/main.py

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from .config import check_initial_setup_state, DB_PATH
from .setup.cert import cert_generate
from datetime import datetime

app = FastAPI(
    title="Korniszon",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# -------------------------
#   MIDDLEWARE
# -------------------------

@app.middleware("http")
async def initial_setup_middleware(request: Request, call_next):
    if request.url == "/api/setup":
        response = await call_next(request)
        return response

    if not check_initial_setup_state():
        return RedirectResponse(url="/api/setup")

    response = await call_next(request)
    return response


# -------------------------
#   SETUP ENDPOINT
# -------------------------

@app.get("/setup")
async def setup_endpoint():
    if check_initial_setup_state():
        return RedirectResponse(url="/docs")
    return {"message": "Initial setup page. Please configure the application."}
