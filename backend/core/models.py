import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, Text

from .database import Base


class LoaderType(str, enum.Enum):
    FABRIC = "fabric"
    FORGE = "forge"
    NEOFORGE = "neoforge"
    VANILLA = "vanilla"


class Server(Base):
    __tablename__ = "servers"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

    mc_version = Column(String, nullable=False)
    loader = Column(Enum(LoaderType), nullable=False)
    port = Column(Integer, nullable=False, default=25565)

    # JVM memory settings (in MB)
    xmx = Column(Integer, default=512, nullable=False)  # Max heap size
    xms = Column(Integer, default=512, nullable=False)  # Min heap size
    cpu_count = Column(Integer, default=1, nullable=False)

    eula = Column(Boolean, default=False, nullable=False)

    # Docker info
    container_id = Column(String, nullable=True, index=True)
    status = Column(String, default="stopped")

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
