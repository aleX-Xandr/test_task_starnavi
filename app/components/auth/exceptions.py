
from fastapi import HTTPException, status

from app.exceptions import DbEntityAlreadyExists


class AuthEntityAlreadyExist(DbEntityAlreadyExists):
    @property
    def entity_name(self) -> str:
        return "Auth"


class AuthException(HTTPException):
    def __init__(
        self,
        detail: str,
        headers={"WWW-Authenticate": "Bearer"},
        status_code=status.HTTP_401_UNAUTHORIZED,
    ):
        super().__init__(
            detail=detail,
            headers=headers,
            status_code=status_code,
        )
