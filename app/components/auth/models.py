from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.components.auth.consts import RolePermissionsEnum
from app.components.base.models import Base


class Auth(Base):
    __tablename__ = "auth"

    id: int | None = Column(
        Integer, primary_key=True, index=True, nullable=False
    )
    created_at: datetime | None = Column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
    login: str = Column(
        String, unique=True, index=True, nullable=False
    )
    hashed_password: str = Column(
        String, nullable=False
    )
    scopes: str = Column(
        String, nullable=False, default=lambda: RolePermissionsEnum.USER
    )
    account_id: int = Column(
        Integer, ForeignKey("accounts.id", ondelete="cascade"), nullable=False
    )
