from fastapi import APIRouter

from src.routers.mc_servers import router as servers_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(servers_router, prefix="/servers", tags=["servers"])

__all__ = ["v1_router"]
