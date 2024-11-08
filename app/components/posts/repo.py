from datetime import datetime
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.sql import and_
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional, List

from app.components.posts.models import Post
from app.exceptions import LogicError


class PostRepository:
    @staticmethod
    async def add_post(tx: AsyncSession, post: Post) -> Post:
        tx.add(post)
        try:
            await tx.flush()
        except IntegrityError:
            raise LogicError("Invalid post data")
        await tx.commit()
        await tx.refresh(post)
        return post

    @staticmethod
    async def get_post(
        tx: AsyncSession, 
        post_id: int, 
        owner_hex_id: Optional[str] = None
    ) -> Post | None:
        q = select(Post).where(and_(
            Post.id == post_id,
            Post.banned == False
        ))
        if owner_hex_id is not None:
            q = q.where(Post.account_hex_id == owner_hex_id)
        raw = await tx.execute(q)
        return raw.scalar_one_or_none()

    @staticmethod
    async def get_posts(
        tx: AsyncSession,
        quantity: int,
        account_hex_id: Optional[str] = None, 
        date_from: Optional[datetime] = None, 
        date_to: Optional[datetime] = None,
    ) -> List[Post]:
        q = select(Post).where(Post.banned == False)

        if account_hex_id is not None:
            q = q.where(Post.account_hex_id == account_hex_id)
        
        if date_from is not None:
            q = q.where(Post.created_at >= date_from)
        
        if date_to is not None:
            q = q.where(Post.created_at <= date_to)

        q = q.order_by(desc(Post.created_at)).limit(quantity)
        raw = await tx.execute(q)
        return raw.scalars().all()

    async def delete_post(self, tx: AsyncSession, post: Post) -> None:
        await tx.delete(post)
        await tx.flush()
