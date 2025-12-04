from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .database import create_db_tables
from .models import ServerInstance
from .routers import servers, auth

from datetime import datetime

app = FastAPI(
    title="Korniszon",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/api/openapi.json",
)


app.include_router(servers.router)
app.include_router(auth.router)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "code": exc.status_code},
    )


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


@app.get("/setup/initdb")
async def init_db():
    create_db_tables()
