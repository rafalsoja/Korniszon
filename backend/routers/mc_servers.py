import logging
from typing import List

from core.crud import (
    create_server,
    delete_server,
    get_all_servers,
    get_server_by_id,
    get_server_by_name,
    get_server_by_port,
    update_server,
    update_server_status,
)
from core.database import get_db
from core.schemas import ServerCreate, ServerResponse, ServerUpdate
from fastapi import APIRouter, Depends, HTTPException
from services.docker_service import DockerService, get_docker_service
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(tags=["servers"])


def ensure_server_exists(server_id: int, db: Session):
    """Ensure server exists or raise HTTPException"""
    server = get_server_by_id(db, server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    return server


@router.get("", response_model=List[ServerResponse])
def list_servers(db: Session = Depends(get_db)):
    """List all servers"""
    servers = get_all_servers(db)
    return servers


@router.post("", response_model=ServerResponse)
def create_server_endpoint(server: ServerCreate, db: Session = Depends(get_db)):
    """Create a new server"""
    # Check if name exists
    existing = get_server_by_name(db, server.name)
    if existing:
        raise HTTPException(
            status_code=400, detail="Server with this name already exists"
        )

    # Check if port is already in use
    port_in_use = get_server_by_port(db, server.port)
    if port_in_use:
        raise HTTPException(
            status_code=400,
            detail=f"Port {server.port} is already in use by server '{port_in_use.name}'",
        )

    new_server = create_server(db, server)
    return new_server


@router.get("/{server_id}", response_model=ServerResponse)
def get_server(server_id: int, db: Session = Depends(get_db)):
    """Get server details"""
    server = ensure_server_exists(server_id, db)
    return server


@router.post("/{server_id}/start")
async def start_server_endpoint(
    server_id: int,
    db: Session = Depends(get_db),
    docker_service: DockerService = Depends(get_docker_service),
):
    """Start a server"""
    server = ensure_server_exists(server_id, db)

    result = await docker_service.start_server(
        server.name,
        server.mc_version,
        server.loader.value,
        server.port,
        server.xmx,
        server.xms,
        server.eula,
    )

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error"])

    update_server_status(db, server, "running", result["container_id"])
    logger.info(f"Started server: {server.name}")
    return {"status": "running", "server_id": server_id}


@router.post("/{server_id}/stop")
async def stop_server_endpoint(
    server_id: int,
    db: Session = Depends(get_db),
    docker_service: DockerService = Depends(get_docker_service),
):
    """Stop a server"""
    server = ensure_server_exists(server_id, db)

    if not server.container_id:
        raise HTTPException(status_code=400, detail="Server not running")

    result = await docker_service.stop_server(server.container_id)

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["error"])

    update_server_status(db, server, "stopped")
    logger.info(f"Stopped server: {server.name}")
    return {"status": "stopped", "server_id": server_id}


@router.delete("/{server_id}")
async def delete_server_endpoint(
    server_id: int,
    db: Session = Depends(get_db),
    docker_service: DockerService = Depends(get_docker_service),
):
    """Delete a server and its container if running"""
    server = ensure_server_exists(server_id, db)

    # Remove Docker container if exists
    if server.container_id:
        result = await docker_service.stop_and_remove_container(server.container_id)
        if result["status"] == "error":
            if "No such container" in result["error"]:
                logger.warning(f"Container already removed: {server.container_id}")
            else:
                raise HTTPException(status_code=500, detail=result["error"])

    # Remove from database
    delete_server(db, server)
    logger.info(f"Deleted server from DB: {server.name}")
    return {"status": "deleted", "server_id": server_id}


@router.patch("/{server_id}", response_model=ServerResponse)
async def update_server_endpoint(
    server_id: int,
    server_update: ServerUpdate,
    db: Session = Depends(get_db),
    restart: bool = False,
):
    """Update server details"""

    server = ensure_server_exists(server_id, db)

    update_server(db, server, server_update)
    logger.info(f"Updated server: {server.name}")

    if restart and server.status == "running":
        logger.info(f"Restarting server after update: {server.name}")
        docker_service = get_docker_service()
        result = await docker_service.restart_server(server.container_id)
        logger.info(f"Server restarted: {server.name}")
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
    return server
