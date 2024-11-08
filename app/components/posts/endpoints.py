from dependency_injector.wiring import inject, Provide
from fastapi import Depends, Path
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from typing import Callable

from app.components.accounts.models import Account
from app.components.accounts.service import AccountService
from app.components.auth.consts import ScopeEnum
from app.components.auth.utils import Scopes
from app.components.posts.models import Post
from app.components.posts.scheme import CreatePostRequest, DeletePostResponse, GetPostRequest, GetPostsRequest, GetPostResponse, GetPostsResponse, UpdatePostRequest
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
        )
    ):
        self._posts_service = posts_service
        self._accounts_service = accounts_service

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
        post = Post(account_hex_id=account.hex_id, text=payload.text)
        async with db_session() as tx:
            post = await self._posts_service.add_post(tx, post)
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
        if payload.owner_hex_id is not None:
            async with db_session() as tx:
                posts_owner = await self._accounts_service.get_account_by_id(
                    tx, account_hex_id=payload.owner_hex_id
                )
            if posts_owner is None:
                raise LogicError("Invalid owner id")
        async with db_session() as tx:
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
            if post is not None:
                post.text = payload.text
                return GetPostResponse.from_model(post)
        raise LogicError(f"Post not found")
    
    @posts_router.delete(
        "/post/{post_id}",
        response_model=DeletePostResponse,
        description="Delete a post by id"
    )
    @inject
    async def delete_post(
        self,
        post_id: int = Path(..., title="Unique id that corresponds to post."),
        account: Account = Scopes(ScopeEnum.POSTS_UPDATE),
        db_session: Callable = Depends(Provide[Container.db_session]),
    ) -> GetPostResponse:
        async with db_session() as tx:
            post = await self._posts_service.get_post(
                tx, post_id, account.hex_id
            )
            if post is not None:
                await self._posts_service.delete_post(tx, post)
                return DeletePostResponse(status="Ok")
        raise LogicError(f"Post not found")

container.wire(modules=[__name__])
