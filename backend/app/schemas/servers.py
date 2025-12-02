from pydantic import BaseModel
from typing import Annotated, Optional
from datetime import datetime


class ServerInstanceBase(BaseModel):
    name: str
    port: int
    status: str = "stopped"
    image_name: str = "mcserver"
    container_id: str | None = None
    jre_version: str
    engine: str
    engine_version: str
    cpu_limit: int = 1
    memory_limit_mb: int = 2048


class ServerInstanceCreate(ServerInstanceBase):
    pass


class ServerInstanceUpdate(BaseModel):
    name: Optional[str] = None
    port: Optional[int] = None
    status: Optional[str] = None
    image_name: Optional[str] = None
    container_id: Optional[str] = None
    jre_version: Optional[str] = None
    engine: Optional[str] = None
    engine_version: Optional[str] = None
    cpu_limit: Optional[int] = None
    memory_limit_mb: Optional[int] = None


class ServerInstance(ServerInstanceBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True