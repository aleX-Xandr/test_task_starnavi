from aiocache import cached
from dependency_injector.wiring import Provide, inject
from fastapi.params import Depends, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt, JWTError
from loguru import logger
from typing import Callable, Sequence

from app.components.auth.consts import ScopeEnum, RolePermissionsEnum, RoleEnum
from app.configs import AuthConfig
from app.containers import Container, container
from app.components.auth.models import Auth
from app.components.auth.repo import AuthRepository
from app.components.auth.exceptions import AuthException
from app.components.accounts.models import Account
from app.components.accounts.repo import AccountRepository


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    scopes={
        ScopeEnum.ACCOUNT_GET: "Get my account info",

        ScopeEnum.POSTS_GET: "Get last posts",
        ScopeEnum.POSTS_CREATE: "Create new post",

        ScopeEnum.COMMENTS_GET: "Get last comments by post",
        ScopeEnum.COMMENTS_CREATE: "Create new comment",

        ScopeEnum.STATISTICS_GET: "Get statistics by post",
    },
    auto_error=False
)


class Scopes(Security):
    def __init__(
        self,
        scopes: str | Sequence[str],
        *,
        use_cache: bool = True,
    ):
        scopes = [scopes] if isinstance(scopes, str) else scopes
        super().__init__(dependency=check_auth, scopes=scopes, use_cache=use_cache)

@cached(ttl=60 * 5)  # 5 minutes ttl
async def _get_account_cached(
    account_id: int,
    db_session: Callable = Depends(Provide[Container.db_session]),
    account_repo: AccountRepository = Depends(Provide[Container.accounts_repository]),
) -> Account | None:
    async with db_session() as tx:
        return await account_repo.get_account_by_id(tx, account_id)

@cached(ttl=60 * 5)  # 5 minutes ttl
async def _get_auth_cached(
    account_id: str,
    db_session: Callable = Depends(Provide[Container.db_session]),
    auth_repo: AuthRepository = Depends(Provide[Container.auth_repository]),
) -> Auth | None:
    async with db_session() as tx:
        return await auth_repo.get_auth_by_account_id(tx, account_id)

@inject
async def check_auth(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    config: AuthConfig = Depends(Provide[Container.config.provided.auth]),
) -> Account:
    credentials_exception = AuthException(
        detail="Could not validate credentials",
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
    except JWTError:
        raise credentials_exception
    account_id = payload.get("account_id")
    if account_id is None:
        raise credentials_exception
    token_scopes = payload.get("scopes")
    if token_scopes is None:
        raise credentials_exception
    required_scopes_left = {*security_scopes.scopes} - {*token_scopes.split(" ")}
    is_enough = check_scopes(token_scopes, " ".join(security_scopes.scopes))
    if not is_enough:
        logger.error(
            f"Not enough permissions: {' '.join(required_scopes_left)} account_id: {account_id}"
        )
        raise AuthException(
            detail=f"Not enough permissions: {' '.join(required_scopes_left)}",
        )
    account = await _get_account_cached(account_id)
    if account is None:
        raise credentials_exception
    return account

def check_scopes(token_scopes: str, required_scopes: str):
    if token_scopes == "*:*":
        return True
    rscopes = required_scopes.split(" ")
    for scope in token_scopes.split(" "):
        if not rscopes:
            return True
        group, func = scope.split(":")
        cur_rscope_i = 0
        while cur_rscope_i < len(rscopes):
            rgroup, rfunc = rscopes[cur_rscope_i].split(":")
            if group not in ("*", rgroup) or func not in ("*", rfunc):
                cur_rscope_i += 1
            else:
                del rscopes[cur_rscope_i]

    return not rscopes

def find_role(auth: Auth) -> RoleEnum:
    for _role in RolePermissionsEnum:
        if auth.scopes == _role.value:
            return RoleEnum[_role.name]
        return RoleEnum.USER


container.wire(modules=[__name__])
