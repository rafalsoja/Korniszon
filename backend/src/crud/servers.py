import asyncio
from sqlalchemy.orm import Session

from src import models
from src.schemas.servers import ServerInstanceCreate, ServerInstanceUpdate
from src.utils.server_instances import deploy_server


async def get_server_instances(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ServerInstance).offset(skip).limit(limit).all()


async def get_server_instance(db: Session, server_id: int):
    return (
        db.query(models.ServerInstance)
        .filter(models.ServerInstance.id == server_id)
        .first()
    )


async def create_server_instance(db: Session, server: ServerInstanceCreate):
    data = server.dict()
    data.pop("status", None)

    db_server = models.ServerInstance(**data, status="pending")
    db.add(db_server)
    db.commit()
    db.refresh(db_server)

    asyncio.create_task(deploy_server(db_server, db))
    return db_server


async def update_server_instance(
    db: Session, server_id: int, server: ServerInstanceUpdate
):
    db_server = await get_server_instance(db, server_id)
    if not db_server:
        return None

    for key, value in server.dict(exclude_unset=True).items():
        setattr(db_server, key, value)

    db.commit()
    db.refresh(db_server)
    return db_server


async def delete_server_instance(db: Session, server_id: int):
    db_server = await get_server_instance(db, server_id)
    if not db_server:
        return None

    db.delete(db_server)
    db.commit()
    return db_server
