from pydantic import BaseModel
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
    status: str | None = None
    cpu_limit: int | None = None
    memory_limit_mb: int | None = None

class ServerInstance(ServerInstanceBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
