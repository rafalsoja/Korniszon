import logging

from sqlalchemy.orm import Session

from .models import Server
from .schemas import ServerCreate, ServerUpdate

logger = logging.getLogger(__name__)


def get_all_servers(db: Session):
    """Get all servers"""
    servers = db.query(Server).all()

    return servers


def get_server_by_id(db: Session, server_id: int):
    """Get server by ID"""
    return db.query(Server).filter(Server.id == server_id).first()


def get_server_by_name(db: Session, name: str):
    """Get server by name"""
    return db.query(Server).filter(Server.name == name).first()


def get_server_by_port(db: Session, port: int):
    """Get server by port"""
    return db.query(Server).filter(Server.port == port).first()


def create_server(db: Session, server: ServerCreate):
    """Create a new server"""
    db_server = Server(
        name=server.name,
        mc_version=server.mc_version,
        loader=server.loader,
        port=server.port,
        description=server.description,
        status="stopped",
        xmx=server.xmx,
        xms=server.xms,
        eula=server.eula,
    )
    db.add(db_server)
    db.commit()
    db.refresh(db_server)
    logger.info(f"Created server: {server.name}")
    return db_server


def update_server_status(
    db: Session, server: Server, status: str, container_id: str = None
):
    """Update server status and container ID"""
    server.status = status
    if container_id:
        server.container_id = container_id
    db.commit()
    db.refresh(server)
    return server


def update_server(db: Session, server: Server, data: ServerUpdate | dict):
    if not isinstance(data, dict):
        data = data.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(server, key, value)

    db.commit()
    db.refresh(server)
    logger.info(f"Updated server: {server.name}")
    return server


def delete_server(db: Session, server: Server):
    """Delete a server from database"""
    db.delete(server)
    db.commit()
    logger.info(f"Deleted server: {server.name}")
