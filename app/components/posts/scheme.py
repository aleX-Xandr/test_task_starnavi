from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

from app.components.posts.models import Post


class CreatePostRequest(BaseModel):
    text: str = Field(
        ..., min_length=1, max_length=1024, description="Text of post"
    )
    auto_comment_timeout: int | None = Field(
        None, ge=0, 
        description="Number of seconds to wait before answer will be shown."
    )


class GetPostRequest(BaseModel):
    post_id: int = Field(..., gt=0, description="Unical ID of the post")


class UpdatePostRequest(GetPostRequest, CreatePostRequest):
    pass


class GetPostsRequest(BaseModel):
    quantity: Optional[int] = Field(
        50, ge=1, le=100, description="Number of posts to retrieve, "\
                                    "default is 50 if not provided."
    )
    owner_hex_id: Optional[str] = Field(
        None, pattern=r'^[a-fA-F0-9]{16}$',
        description="Owner's hexadecimal ID."
    )


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
