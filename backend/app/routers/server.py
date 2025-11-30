from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/servers", tags=["servers"])


@router.post("/", response_model=schemas.ServerInstance)
def create_server(server: schemas.ServerInstanceCreate, db: Session = Depends(get_db)):
    return crud.create_server_instance(db, server)


@router.get("/", response_model=list[schemas.ServerInstance])
def read_servers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_server_instances(db, skip=skip, limit=limit)


@router.get("/{server_id}", response_model=schemas.ServerInstance)
def read_server(server_id: int, db: Session = Depends(get_db)):
    db_server = crud.get_server_instance(db, server_id)
    if db_server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return db_server


@router.put("/{server_id}", response_model=schemas.ServerInstance)
def update_server(
    server_id: int, server: schemas.ServerInstanceUpdate, db: Session = Depends(get_db)
):
    db_server = crud.update_server_instance(db, server_id, server)
    if db_server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return db_server


@router.delete("/{server_id}", response_model=schemas.ServerInstance)
def delete_server(server_id: int, db: Session = Depends(get_db)):
    db_server = crud.delete_server_instance(db, server_id)
    if db_server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return db_server
