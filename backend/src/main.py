from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from src.database import create_db_tables
from src.routers.servers import servers_router
from src.routers.auth import auth_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_tables()
    yield


app = FastAPI(
    title="Korniszon",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.include_router(servers_router)
app.include_router(auth_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "code": exc.status_code},
    )
