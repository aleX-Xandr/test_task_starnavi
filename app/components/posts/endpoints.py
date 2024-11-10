from dependency_injector.wiring import inject, Provide
from fastapi import Depends, Path
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from typing import Callable

from app.components.accounts.models import Account
from app.components.accounts.service import AccountService
from app.components.auth.consts import ScopeEnum
from app.components.auth.utils import Scopes
from app.components.gemini.service import GeminiService
from app.components.posts.models import Post
from app.components.posts.scheme import (
    CreatePostRequest,
    DeletePostResponse,
    GetPostRequest,
    GetPostsRequest,
    GetPostResponse,
    GetPostsResponse,
    UpdatePostRequest
)
from app.components.posts.service import PostService
from app.containers import Container, container
from app.exceptions import LogicError

posts_router = InferringRouter()


@cbv(posts_router)
class PostsAPI:
    @inject
    def __init__(
        self,
        posts_service: PostService = Depends(
            Provide[Container.posts_service]
        ),
        accounts_service: AccountService = Depends(
            Provide[Container.accounts_service]
        ),
        gemini_service: GeminiService = Depends(
            Provide[Container.gemini_service]
        )
    ):
        self._accounts_service = accounts_service
        self._gemini_service = gemini_service
        self._posts_service = posts_service

    @posts_router.post(
        "/post",
        response_model=GetPostResponse,
        description="Post will be created if text is valid"
    )
    @inject
    async def create_post(
        self,
        payload: CreatePostRequest,
        account: Account = Scopes(ScopeEnum.POSTS_CREATE),
        db_session: Callable = Depends(Provide[Container.db_session]),
    ) -> GetPostResponse:
        post = Post(
            account_hex_id=account.hex_id, 
            text=payload.text, 
            auto_comment_timeout=payload.auto_comment_timeout
        )
        result = await self._gemini_service.analyze_text(post.text)
        if isinstance(result, bool):
            post.banned = not result
        async with db_session() as tx:
            post = await self._posts_service.add_post(tx, post)
        if post.banned:
            raise LogicError("Post was banned!")
        return GetPostResponse.from_model(post)

    @posts_router.get(
        "/post",
        response_model=GetPostResponse,
        description="Returns a post by id"
    )
    @inject
    async def get_post(
        self,
        payload: GetPostRequest = Depends(),
        account: Account = Scopes(ScopeEnum.POSTS_GET),
        db_session: Callable = Depends(Provide[Container.db_session]),
    ) -> GetPostResponse:
        async with db_session() as tx:
            post = await self._posts_service.get_post(
                tx,
                payload.post_id
            )
        if not post:
            raise LogicError(f"Post not found")
        return GetPostResponse.from_model(post)

    @posts_router.get(
        "/posts",
        response_model=GetPostsResponse,
        description="Returns a selection of posts"
    )
    @inject
    async def get_posts(
        self,
        payload: GetPostsRequest = Depends(),
        account: Account = Scopes(ScopeEnum.POSTS_GET),
        db_session: Callable = Depends(Provide[Container.db_session]),
    ) -> GetPostsResponse:
        async with db_session() as tx:
            if payload.owner_hex_id is not None:
                posts_owner = await self._accounts_service.get_account(
                    tx, account_hex_id=payload.owner_hex_id
                )
                if posts_owner is None:
                    raise LogicError("Invalid owner id")
            posts = await self._posts_service.get_posts(tx, payload)
            return GetPostsResponse(
                posts = [GetPostResponse.from_model(post) for post in posts]
            )

    @posts_router.put(
        "/post",
        response_model=GetPostResponse,
        description="Updates a post by id"
    )
    @inject
    async def update_post(
        self,
        payload: UpdatePostRequest,
        account: Account = Scopes(ScopeEnum.POSTS_UPDATE),
        db_session: Callable = Depends(Provide[Container.db_session]),
    ) -> GetPostResponse:
        async with db_session() as tx:
            post = await self._posts_service.get_post(
                tx,
                payload.post_id
            )
            if post is None:
                raise LogicError(f"Post not found")
            result = await self._gemini_service.analyze_text(payload.text)
            if isinstance(result, bool):
                post.banned = not result
            post.text = payload.text
            if payload.auto_comment_timeout is not None:
                post.auto_comment_timeout = payload.auto_comment_timeout
        if post.banned:
            raise LogicError("Post was banned!")
        return GetPostResponse.from_model(post)
    
    @posts_router.delete(
        "/post/{post_id}",
        response_model=DeletePostResponse,
        description="Delete a post by id"
    )
    @inject
    async def delete_post(
        self,
        post_id: int = Path(..., title="Unique id that corresponds to post."),
        account: Account = Scopes(ScopeEnum.POSTS_DELETE),
        db_session: Callable = Depends(Provide[Container.db_session]),
    ) -> GetPostResponse:
        async with db_session() as tx:
            post = await self._posts_service.get_post(
                tx, post_id, account.hex_id
            )
            if post is None:
                raise LogicError(f"Post not found")
            await self._posts_service.delete_post(tx, post)
            return DeletePostResponse(status="Ok")

container.wire(modules=[__name__])
