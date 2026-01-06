from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime


class ServerInstanceBase(BaseModel):
    name: str = Field(min_length=3)
    port: int = Field(ge=25565, le=65535)
    image_name: str
    mc_version: Literal[
        "1.12.2",
        "1.16.5",
        "1.17",
        "1.18.2",
        "1.19.4",
        "1.20.1",
        "1.21",
        "1.21.1",
        "1.21.10",
    ]
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
    image_name: Optional[str] = None
    mc_version: Optional[
        Literal[
            "1.12.2",
            "1.16.5",
            "1.17",
            "1.18.2",
            "1.19.4",
            "1.20.1",
            "1.21",
            "1.21.1",
            "1.21.10",
        ]
    ] = None
    jre_version: Optional[Literal["8", "11", "17", "21"]] = None
    engine: Optional[Literal["fabric", "forge", "neoforge", "vanilla"]] = None
    engine_version: Optional[str] = None
    cpu_limit: Optional[int] = None
    memory_limit_mb: Optional[int] = None


class ServerInstance(ServerInstanceBase):
    id: int
    status: Literal["pending", "installing", "stopped", "running", "error"]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
