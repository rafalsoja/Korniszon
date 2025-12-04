from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud
from ..schemas import servers
from ..database import get_db
from ..routers.auth import get_current_user

router = APIRouter(prefix="/servers", tags=["servers"])


@router.post("/", response_model=servers.ServerInstance)
async def create_server(
    server: servers.ServerInstanceCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await crud.create_server_instance(db, server)


@router.get("/", response_model=list[servers.ServerInstance])
async def read_servers(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await crud.get_server_instances(db)


@router.get("/{server_id}", response_model=servers.ServerInstance)
async def read_server(
    server_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_server = await crud.get_server_instance(db, server_id)
    if db_server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return db_server


@router.put("/{server_id}", response_model=servers.ServerInstance)
async def update_server(
    server_id: int, 
    server: servers.ServerInstanceUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_server = await crud.update_server_instance(db, server_id, server)
    if db_server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return db_server


@router.delete("/{server_id}", response_model=servers.ServerInstance)
async def delete_server(
    server_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_server = await crud.delete_server_instance(db, server_id)
    if db_server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return db_server