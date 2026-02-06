import logging

import uvicorn
from fastapi import FastAPI

from src.core.database import init_db
from src.core.logger import setup_logging
from src.routers import v1_router

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Korniszon API")

init_db()

app.include_router(v1_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
