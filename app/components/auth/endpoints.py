from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from typing import Callable

from app.components.auth.scheme import GetTokenResponse
from app.components.auth.service import AuthService
from app.components.auth.utils import find_role
from app.containers import Container, container

auth_router = InferringRouter()


@cbv(auth_router)
class AuthAPI:
    @inject
    def __init__(
        self,
        auth_service: AuthService = Depends(Provide[Container.auth_service]),
    ):
        self._auth_service = auth_service

    @auth_router.post(
        "/auth/token",
        response_model=GetTokenResponse
    )
    @inject
    async def get_token(
        self,
        data: OAuth2PasswordRequestForm = Depends(),
        db_session: Callable = Depends(Provide[Container.db_session]),
    ):        
        async with db_session() as tx:
            access_token, expires_in = await self._auth_service.create_token(
                tx, data.username, data.password
            )
            auth = await self._auth_service.get_auth(tx, data.username)

        return GetTokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in * 60, # convert to seconds
            role=find_role(auth)
        )

container.wire(modules=[__name__])
