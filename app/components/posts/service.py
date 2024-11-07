from datetime import datetime, timezone
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional, List

from app.components.posts.models import Post
from app.components.posts.repo import PostRepository


class PostService:
    def __init__(self, posts_repository: PostRepository):
        self._post_repository = posts_repository

    async def add_post(self, tx: AsyncSession, post: Post) -> Post:
        return await self._post_repository.add_post(tx, post)

    async def get_post(self, tx: AsyncSession, post_id: int) -> Post | None:
        return await self._post_repository.get_post_by_id(tx, post_id)
    
    async def get_posts(
        self, 
        tx: AsyncSession, 
        quantity: int,
        account_id: Optional[str] = None, 
        date_from: Optional[datetime] = None, 
        date_to: Optional[datetime] = None,
    ) -> List[Post]:
        now = datetime.now(timezone.utc)
        if date_from is not None:
            if date_from > now:
                return []
            if date_to is not None and date_to < date_from:
                return []
        return await self._post_repository.get_posts(tx, quantity, account_id, date_from, date_to)
