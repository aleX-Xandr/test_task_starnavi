from datetime import datetime
from sqlalchemy import desc, func, select, and_, case
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional, List

from app.components.comments.models import Comment
from app.exceptions import LogicError


class CommentRepository:
    @staticmethod
    async def add_comment(tx: AsyncSession, comment: Comment) -> Comment:
        tx.add(comment)
        try:
            await tx.flush()
        except IntegrityError:
            raise LogicError("Invalid comment data")
        await tx.commit()
        await tx.refresh(comment)
        return comment

    @staticmethod
    async def get_comment(
        tx: AsyncSession, 
        comment_id: int, 
        owner_hex_id: Optional[str] = None
    ) -> Comment | None:
        q = select(Comment).where(and_(
            Comment.id == comment_id,
            Comment.banned == False
        ))
        if owner_hex_id is not None:
            q = q.where(Comment.account_hex_id == owner_hex_id)
        raw = await tx.execute(q)
        return raw.scalar_one_or_none()
    
    @staticmethod
    async def get_comments(
        tx: AsyncSession, 
        post_id: int, 
        quantity: int,
        account_hex_id: Optional[str] = None, 
        date_from: Optional[datetime] = None, 
        date_to: Optional[datetime] = None,
    ) -> List[Comment]:
        q = select(Comment).where(and_(
            Comment.post_id == post_id,
            Comment.banned == False
        ))

        if account_hex_id is not None:
            q = q.where(Comment.account_hex_id == account_hex_id)
        
        if date_from is not None:
            q = q.where(Comment.created_at >= date_from)
        
        if date_to is not None:
            q = q.where(Comment.created_at <= date_to)

        q = q.order_by(desc(Comment.created_at)).limit(quantity)
        raw = await tx.execute(q)
        return raw.scalars().all()

    @staticmethod
    async def get_comments_breakdown(
        tx: AsyncSession,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List:
        q = (
            select(
                func.date(Comment.created_at).label("date"),
                func.sum(case((Comment.banned == False, 1), else_=0)).label("created"),
                func.sum(case((Comment.banned == True, 1), else_=0)).label("blocked"),
            )
            .where(Comment.created_at.between(date_from, date_to))
            .group_by(func.date(Comment.created_at))
            .order_by("date")
        )
        raw = await tx.execute(q)
        return raw.scalars().all()

    @staticmethod
    async def delete_comment(tx: AsyncSession, comment: Comment) -> None:
        await tx.delete(comment)
        await tx.flush()
