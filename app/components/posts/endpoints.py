from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from typing import Callable

from app.components.accounts.models import Account
from app.components.auth.consts import ScopeEnum
from app.components.auth.utils import Scopes
from app.components.posts.models import Post
from app.components.posts.scheme import CreatePostRequest, GetPostResponse
from app.components.posts.service import PostService
from app.containers import Container, container

posts_router = InferringRouter()


@cbv(posts_router)
class PostsAPI:
    @inject
    def __init__(
        self,
        posts_service: PostService = Depends(
            Provide[Container.posts_service]
        )
    ):
        self._posts_service = posts_service

    @posts_router.post(
        "/posts/create",
        response_model=GetPostResponse,
        description="Post will be created if text is valid"
    )
    @inject
    async def create_post(
        self,
        payload: CreatePostRequest,
        account: Account = Scopes(ScopeEnum.POSTS_CREATE),
        db_session: Callable = Depends(Provide[Container.db_session]),
    ):
        post = Post(account_hex_id=account.hex_id, text=payload.text)
        async with db_session() as tx:
            post = await self._posts_service.add_post(tx, post)
            return GetPostResponse(
                created_at=post.created_at,
                account_hex_id=post.account_hex_id,
                text=post.text,
                edited=post.edited,
            )


container.wire(modules=[__name__])
