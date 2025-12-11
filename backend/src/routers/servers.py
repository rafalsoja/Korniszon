from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.crud.servers import (
    create_server_instance,
    get_server_instances,
    get_server_instance,
    update_server_instance,
    delete_server_instance,
)
from src.schemas.servers import (
    ServerInstance,
    ServerInstanceCreate,
    ServerInstanceUpdate,
)
from src.database import get_db
from src.routers.auth import get_current_user

servers_router = APIRouter(prefix="/servers", tags=["servers"])


@servers_router.post("/", response_model=ServerInstance)
async def create_server(
    server: ServerInstanceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await create_server_instance(db, server)


@servers_router.get("/", response_model=list[ServerInstance])
async def read_servers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_server_instances(db, skip=skip, limit=limit)


@servers_router.get("/{server_id}", response_model=ServerInstance)
async def read_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_server = await get_server_instance(db, server_id)
    if db_server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return db_server


@servers_router.put("/{server_id}", response_model=ServerInstance)
async def update_server(
    server_id: int,
    server: ServerInstanceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_server = await update_server_instance(db, server_id, server)
    if db_server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return db_server


@servers_router.delete("/{server_id}", response_model=ServerInstance)
async def delete_server(
    server_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_server = await delete_server_instance(db, server_id)
    if db_server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return db_server
