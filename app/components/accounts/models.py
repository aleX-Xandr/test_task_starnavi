from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String

from app.components.base.models import Base
from app.database import UTCNow


class Account(Base):
    __tablename__ = "accounts"

    id: int | None = Column(
        Integer, primary_key=True, index=True, nullable=False, unique=True
    )
    created_at: datetime | None = Column(
        DateTime, server_default=UTCNow(), nullable=False
    )
    hex_id: str | None = Column(
        String(32), nullable=False, unique=True
    )
    login: str | None = Column(
        String, unique=True, index=True, nullable=False
    )
