from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator

VERSION_PATTERN = r"^1\.[0-2]?[0-9](\.[0-1]?[0-9])?$"


class ServerStatus(str, Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"


class LoaderType(str, Enum):
    FABRIC = "fabric"
    FORGE = "forge"
    NEOFORGE = "neoforge"


class ServerCreate(BaseModel):
    name: str
    mc_version: str = Field(pattern=VERSION_PATTERN, example="1.12.2")
    loader: LoaderType
    port: int = Field(default=25565, ge=1024, le=65535)
    status: ServerStatus = ServerStatus.STOPPED
    description: Optional[str] = None
    xmx: int = Field(default=1024, ge=256, le=16384)  # Max heap size in MB
    xms: int = Field(default=1024, ge=256, le=16384)  # Min heap size in MB
    eula: bool = Field(default=False)

    @model_validator(mode="after")
    def check_xmx_greater_or_equal_xms(self):
        if self.xmx < self.xms:
            raise ValueError("Xmx must be greater than or equal to Xms")
        return self


class ServerUpdate(BaseModel):
    description: Optional[str] = None
    xmx: Optional[int] = Field(None, ge=256, le=16384)
    xms: Optional[int] = Field(None, ge=256, le=16384)
    eula: Optional[bool] = None

    @model_validator(mode="after")
    def check_xmx_greater_or_equal_xms(self):
        if self.xmx is not None and self.xms is not None and self.xmx < self.xms:
            raise ValueError("Xmx must be greater than or equal to Xms")
        return self


class ServerResponse(BaseModel):
    id: int = Field(gt=0)
    name: str
    description: Optional[str] = None
    mc_version: str
    loader: LoaderType
    port: int
    status: ServerStatus
    xmx: int
    xms: int
    cpu_count: int
    eula: bool
    container_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
