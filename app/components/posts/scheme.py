from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

from app.components.posts.models import Post


class CreatePostRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1024)


class GetPostRequest(BaseModel):
    post_id: int = Field(..., gt=0)


class UpdatePostRequest(GetPostRequest, CreatePostRequest):
    pass


class GetPostsRequest(BaseModel):
    quantity: Optional[int] = Field(50, ge=1, le=100, description="Number of posts to retrieve, default is 50 if not provided.")
    owner_hex_id: Optional[str] = Field(None, pattern=r'^[a-fA-F0-9]{16}$', description="Owner's hexadecimal ID.")
    date_from: Optional[datetime] = Field(None, description="Start date for filtering posts.")
    date_to: Optional[datetime] = Field(None, description="End date for filtering posts.")

    @field_validator("date_from", "date_to", mode="before")
    def set_utc_timezone(cls, value):
        if value is None:
            return value
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value


class GetPostResponse(BaseModel):
    id: int
    created_at: datetime
    account_hex_id: str
    text: str
    edited: bool

    @classmethod
    def from_model(cls, model: Post) -> "GetPostResponse":
        return cls(
            id=model.id,
            created_at=model.created_at,
            account_hex_id=model.account_hex_id,
            text=model.text,
            edited=model.edited,
        )


class GetPostsResponse(BaseModel):
    posts: List[GetPostResponse]


class DeletePostResponse(BaseModel):
    status: str
