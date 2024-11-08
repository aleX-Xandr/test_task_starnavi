from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey

from app.components.base.models import Base


class Comment(Base):
    __tablename__ = "comments"

    id: int | None = Column(
        "id", Integer, primary_key=True, index=True, nullable=False
    )
    created_at: datetime | None = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    account_hex_id: str = Column(
        String(32), ForeignKey("accounts.hex_id"), 
        nullable=False
    )
    post_id: str = Column(
        String(32), ForeignKey("posts.id", ondelete="cascade"), 
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