from datetime import timedelta, datetime, timezone
from typing import Tuple

from jose import jwt
from passlib.context import CryptContext
from sqlmodel.ext.asyncio.session import AsyncSession

from app.components.auth.models import Auth
from app.components.auth.repo import AuthRepository
from app.configs import AuthConfig
from app.exceptions import LogicError


class AuthService:
    def __init__(
        self,
        config: AuthConfig,
        auth_repository: AuthRepository,
        crypt_context: CryptContext,
    ):
        self._config = config
        self._auth_repository = auth_repository
        self._pwd_context = crypt_context

    async def add_auth(self, tx: AsyncSession, auth: Auth) -> Auth:
        return await self._auth_repository.add_auth(tx, auth)

    async def get_auth(self, tx: AsyncSession, login: str) -> Auth | None:
        return await self._auth_repository.get_auth(tx, login)

    async def create_token(
        self, tx: AsyncSession, login: str, password: str
    ) -> Tuple[str, float]:
        auth = await self._auth_repository.get_auth(tx, login)
        if not auth:
            raise LogicError(f"Account {login} doesn't exist")

        if not self._pwd_context.verify(password, auth.hashed_password):
            raise LogicError("Invalid auth credentials")

        expires_delta = timedelta(minutes=self._config.token_expiration_minutes)
        data = {
            "auth_id": auth.id,
            "account_id": auth.account_id,
            "scopes": auth.scopes,
        }
        if expires_delta:
            expire = datetime.now() + expires_delta
            data["exp"] = expire
        access_token = jwt.encode(
            data, self._config.secret_key, algorithm=self._config.algorithm
        )
        return access_token, self._config.token_expiration_minutes
