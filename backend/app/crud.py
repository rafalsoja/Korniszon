import asyncio
from sqlalchemy.orm import Session
from . import models
from .schemas import servers
from .utils.server_instances import deploy_server


async def get_server_instances(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ServerInstance).offset(skip).limit(limit).all()


async def get_server_instance(db: Session, server_id: int):
    return (
        db.query(models.ServerInstance)
        .filter(models.ServerInstance.id == server_id)
        .first()
    )


async def create_server_instance(db: Session, server: servers.ServerInstanceCreate):
    db_server = models.ServerInstance(**server.dict())
    db.add(db_server)
    db.commit()
    db.refresh(db_server)

    asyncio.create_task(deploy_server(db_server))
    return db_server


async def update_server_instance(
    db: Session, server_id: int, server: servers.ServerInstanceUpdate
):
    db_server = get_server_instance(db, server_id)
    if not db_server:
        return None
    for key, value in server.dict(exclude_unset=True).items():
        setattr(db_server, key, value)
    db.commit()
    db.refresh(db_server)
    return db_server


async def delete_server_instance(db: Session, server_id: int):
    db_server = get_server_instance(db, server_id)
    if not db_server:
        return None
    db.delete(db_server)
    db.commit()
    return db_server
