from datetime import datetime, timezone
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional, List

from app.components.posts.models import Post
from app.components.posts.repo import PostRepository
from app.components.posts.scheme import CreatePostRequest, GetPostRequest, GetPostsRequest


class PostService:
    def __init__(self, posts_repository: PostRepository):
        self._post_repository = posts_repository

    async def add_post(self, tx: AsyncSession, post: Post) -> Post:
        return await self._post_repository.add_post(tx, post)

    async def get_post(self, tx: AsyncSession, post_id: int, owner_hex_id: Optional[str] = None) -> Post | None:
        return await self._post_repository.get_post(tx, post_id, owner_hex_id)
    
    async def get_posts(
        self, 
        tx: AsyncSession, 
        payload: GetPostsRequest
    ) -> List[Post]:
        if payload.date_from is not None:
            now = datetime.now(timezone.utc)
            if payload.date_from > now:
                return []
            if payload.date_to is not None and payload.date_to < payload.date_from:
                return []
            
        return await self._post_repository.get_posts(
            tx, 
            quantity=payload.quantity, 
            account_hex_id=payload.owner_hex_id, 
            date_from=payload.date_from, 
            date_to=payload.date_to
        )
    
    async def delete_post(self, tx: AsyncSession, post: Post) -> None:
        await self._post_repository.delete_post(tx, post)