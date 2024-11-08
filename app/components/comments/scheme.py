from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

from app.components.comments.models import Comment


class CreateCommentRequest(BaseModel):
    post_id: int = Field(..., gt=0)
    text: str = Field(..., min_length=1, max_length=1024)


class GetCommentRequest(BaseModel):
    comment_id: int = Field(..., gt=0)


class UpdateCommentRequest(BaseModel):
    comment_id: int = Field(..., gt=0)
    text: str = Field(..., min_length=1, max_length=1024)


class GetCommentsRequest(BaseModel):
    post_id: Optional[int] = Field(..., description="ID to fetch comments by post")
    quantity: Optional[int] = Field(50, ge=1, le=100, description="Number of comments to retrieve, default is 50 if not provided.")
    owner_hex_id: Optional[str] = Field(None, pattern=r'^[a-fA-F0-9]{16}$', description="Owner's hexadecimal ID.")
    date_from: Optional[datetime] = Field(None, description="Start date for filtering comments.")
    date_to: Optional[datetime] = Field(None, description="End date for filtering comments.")


class GetCommentResponse(BaseModel):
    id: int
    created_at: datetime
    account_hex_id: str
    post_id: int
    text: str
    edited: bool

    @classmethod
    def from_model(cls, model: Comment) -> "GetCommentResponse":
        return cls(
            id=model.id,
            created_at=model.created_at,
            account_hex_id=model.account_hex_id,
            post_id=model.post_id,
            text=model.text,
            edited=model.edited,
        )


class GetCommentsResponse(BaseModel):
    comments: List[GetCommentResponse]


class DeleteCommentResponse(BaseModel):
    status: str
