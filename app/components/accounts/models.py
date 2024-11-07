from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String

from app.components.base.models import Base


class Account(Base):
    __tablename__ = "accounts"

    id: int | None = Column("id", Integer, primary_key=True, index=True, nullable=False)
    created_at: datetime | None = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    hex_id: str | None = Column(String(32), nullable=False)
    login: str | None = Column(String, unique=True, index=True, nullable=False)
    
    # it`s possible to add extra fields like name, email, etc.
