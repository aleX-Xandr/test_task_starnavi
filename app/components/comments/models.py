from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey

from app.components.base.models import Base
from app.database import UTCNow


class Comment(Base):
    __tablename__ = "comments"

    id: int | None = Column(
        Integer, primary_key=True, index=True, nullable=False, unique=True
    )
    created_at: datetime | None = Column(
        DateTime, server_default=UTCNow(), nullable=False
    )
    account_hex_id: str = Column(
        String(32), ForeignKey("accounts.hex_id"), 
        nullable=False
    )
    post_id: int = Column(
        Integer, ForeignKey("posts.id", ondelete="cascade"), 
        nullable=False
    )
    text: str = Column(
        String, nullable=False
    )
    edited: bool = Column(
        Boolean, nullable=False, default=False
    )
    banned: bool = Column(
        Boolean, nullable=False, default=False
    )