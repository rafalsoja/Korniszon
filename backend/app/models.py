from sqlalchemy import Column, Integer, String, DateTime
from .database import Base
from datetime import datetime


class ServerInstance(Base):
    __tablename__ = "server_instance"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    port = Column(Integer, unique=True, index=True, nullable=False, default=25565)
    status = Column(String, nullable=False, default="stopped")
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    image_name = Column(String, nullable=False, default="mcserver")
    container_id = Column(String, unique=True, index=True, nullable=True)
    jre_version = Column(String, nullable=False)

    engine = Column(String, nullable=False)
    engine_version = Column(String, nullable=False)

    cpu_limit = Column(Integer, nullable=False, default=1)
    memory_limit_mb = Column(Integer, nullable=False, default=2048)
