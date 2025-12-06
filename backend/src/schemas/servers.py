from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated, Optional, Literal
from datetime import datetime


class ServerInstanceBase(BaseModel):
    name: str
    port: Annotated[int, Field(ge=25565, le=65535)]
    status: Literal["stopped", "running", "error"] = "stopped"
    image_name: str
    container_id: str | None = None
    mc_version: Literal["1.12.2", "1.16.5", "1.17", "1.18.2", "1.19.4", "1.20.1", "1.21", "1.21.1", "1.21.10"]
    jre_version: Literal["8", "11", "17", "21"]
    engine: Literal["fabric", "forge", "neoforge", "vanilla"]
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
    mc_version: Optional[str] = None
    jre_version: Optional[str] = None
    engine: Optional[str] = None
    engine_version: Optional[str] = None
    cpu_limit: Optional[int] = None
    memory_limit_mb: Optional[int] = None


class ServerInstance(ServerInstanceBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)