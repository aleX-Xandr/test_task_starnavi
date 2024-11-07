from pydantic import BaseModel

from app.components.accounts.models import Account
from app.components.auth.consts import RoleEnum


class GetAccountResponse(BaseModel):
    created: bool
