from datetime import datetime
from pydantic import BaseModel, Field


class CreatePostRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1024)


class GetPostResponse(BaseModel):
    created_at: datetime
    account_hex_id: str
    text: str
    edited: bool
