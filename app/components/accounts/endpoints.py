import secrets

from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from passlib.context import CryptContext
from typing import Callable

from app.components.accounts.models import Account
from app.components.accounts.scheme import GetAccountResponse
from app.components.accounts.service import AccountService
from app.components.auth.models import Auth
from app.components.auth.service import AuthService
from app.containers import Container, container

accounts_router = InferringRouter()


@cbv(accounts_router)
class AccountsAPI:
    @inject
    def __init__(
        self,
        accounts_service: AccountService = Depends(
            Provide[Container.accounts_service]
        ),
        auth_service: AuthService = Depends(
            Provide[Container.auth_service]
        ),
        crypt_context: CryptContext = Depends(
            Provide[Container.crypt_context]
        ),
    ):
        self._accounts_service = accounts_service
        self._auth_service = auth_service
        self._crypt_context = crypt_context

    @accounts_router.post(
        "/accounts/register",
        response_model=GetAccountResponse,
        description="Account will be created if registration data is valid"
    )
    @inject
    async def create_account(
        self,
        data: OAuth2PasswordRequestForm = Depends(),
        db_session: Callable = Depends(Provide[Container.db_session]),
    ) -> GetAccountResponse:
        account = Account(login=data.username, hex_id=secrets.token_hex(16))
        async with db_session() as tx:
            account = await self._accounts_service.add_account(tx, account)
            hashed_pwd = self._crypt_context.hash(data.password)
            auth = Auth(
                account_id=account.id,
                login=data.username,
                hashed_password=hashed_pwd
            )
            auth = await self._auth_service.add_auth(tx, auth)
        return GetAccountResponse(created=True)

container.wire(modules=[__name__])
