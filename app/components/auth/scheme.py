from pydantic import BaseModel

from app.components.auth.consts import RoleEnum


class GetTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: float
    role: RoleEnum
