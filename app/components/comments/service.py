from datetime import datetime, timezone
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional, List, Dict

from app.components.comments.models import Comment
from app.components.comments.repo import CommentRepository
from app.components.comments.scheme import GetCommentsRequest, GetCommentsBreakdownRequest


class CommentService:
    def __init__(self, comments_repository: CommentRepository):
        self._comments_repository = comments_repository

    async def add_comment(self, tx: AsyncSession, comment: Comment) -> Comment:
        return await self._comments_repository.add_comment(tx, comment)

    async def get_comment(self, tx: AsyncSession, comment_id: int, owner_hex_id: Optional[str] = None) -> Comment | None:
        return await self._comments_repository.get_comment(tx, comment_id, owner_hex_id)
    
    async def get_comments(
        self, 
        tx: AsyncSession, 
        payload: GetCommentsRequest
    ) -> List[Comment]:
        if payload.date_from is not None:
            now = datetime.now()
            if payload.date_from > now:
                return []
            if payload.date_to is not None and payload.date_to < payload.date_from:
                return []
            
        return await self._comments_repository.get_comments(
            tx, 
            post_id=payload.post_id, 
            quantity=payload.quantity, 
            account_hex_id=payload.owner_hex_id, 
            date_from=payload.date_from, 
            date_to=payload.date_to
        )
    
    async def get_comments_breakdown(
        self,
        tx: AsyncSession,
        payload: GetCommentsBreakdownRequest
    ) -> List[Dict]:
        if payload.date_from is not None:
            now = datetime.now()
            if payload.date_from > now:
                return []
            if payload.date_to is not None and payload.date_to < payload.date_from:
                return []
            
        return await self._comments_repository.get_comments_breakdown(
            tx,
            date_from=payload.date_from,
            date_to=payload.date_to
        )
    
    async def delete_comment(self, tx: AsyncSession, comment: Comment) -> None:
        await self._comments_repository.delete_comment(tx, comment)