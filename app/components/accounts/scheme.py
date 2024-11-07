from pydantic import BaseModel


class GetAccountResponse(BaseModel):
    created: bool
