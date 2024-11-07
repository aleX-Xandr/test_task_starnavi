from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.components.auth.exceptions import AuthEntityAlreadyExist
from app.components.auth.models import Auth


class AuthRepository:
    @staticmethod
    async def add_auth(tx: AsyncSession, auth: Auth) -> Auth:
        tx.add(auth)
        try:
            await tx.flush()
        except IntegrityError as e:
            raise AuthEntityAlreadyExist(auth.login)
        await tx.refresh(auth)
        return auth

    @staticmethod
    async def get_auth(tx: AsyncSession, login: str) -> Auth | None:
        q = select(Auth).where(Auth.login == login)
        raw = await tx.execute(q)
        return raw.scalar_one_or_none()

    @staticmethod
    async def get_auth_by_account_id(
        tx: AsyncSession, account_id: str
    ) -> Auth | None:
        q = select(Auth).where(Auth.account_id == account_id)
        raw = await tx.execute(q)
        return raw.scalar_one_or_none()
