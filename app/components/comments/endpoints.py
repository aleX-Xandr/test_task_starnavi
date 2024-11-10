from dependency_injector.wiring import inject, Provide
from fastapi import Depends, Path
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from typing import Callable

from app.components.accounts.models import Account
from app.components.accounts.service import AccountService
from app.components.auth.consts import ScopeEnum
from app.components.auth.utils import Scopes
from app.components.comments.models import Comment
from app.components.comments.scheme import (
    CreateCommentRequest,
    DailyBreakdown,
    DeleteCommentResponse,
    GetCommentRequest,
    GetCommentResponse,
    GetCommentsBreakdownRequest,
    GetCommentsBreakdownResponse,
    GetCommentsRequest,
    GetCommentsResponse,
    UpdateCommentRequest
)
from app.components.comments.service import CommentService
from app.components.posts.models import Post
from app.components.posts.service import PostService
from app.containers import Container, container
from app.exceptions import LogicError

comments_router = InferringRouter()


@cbv(comments_router)
class CommentsAPI:
    @inject
    def __init__(
        self,
        comments_service: CommentService = Depends(
            Provide[Container.comments_service]
        ),
        accounts_service: AccountService = Depends(
            Provide[Container.accounts_service]
        ),
        posts_service: PostService = Depends(
            Provide[Container.posts_service]
        ),
    ):
        self._accounts_service = accounts_service
        self._comments_service = comments_service
        self._posts_service = posts_service

    @comments_router.post(
        "/comment",
        response_model=GetCommentResponse,
        description="Comment will be created if post id and text is valid"
    )
    @inject
    async def create_comment(
        self,
        payload: CreateCommentRequest,
        account: Account = Scopes(ScopeEnum.COMMENTS_CREATE),
        db_session: Callable = Depends(Provide[Container.db_session]),
    ) -> GetCommentResponse:
        async with db_session() as tx:
            post = await self._posts_service.get_post(
                tx,
                payload.post_id
            )
            if not post:
                raise LogicError(f"Post not found")
            comment = Comment(
                account_hex_id=account.hex_id,
                post_id=post.id,
                text=payload.text
            )
            comment = await self._comments_service.add_comment(tx, comment)
        return GetCommentResponse.from_model(comment)

    @comments_router.get(
        "/comment",
        response_model=GetCommentResponse,
        description="Returns a comment by id"
    )
    @inject
    async def get_comment(
        self,
        payload: GetCommentRequest = Depends(),
        account: Account = Scopes(ScopeEnum.COMMENTS_GET),
        db_session: Callable = Depends(Provide[Container.db_session]),
    ) -> GetCommentResponse:
        async with db_session() as tx:
            comment = await self._comments_service.get_comment(
                tx,
                payload.comment_id
            )
        if not comment:
            raise LogicError(f"Comment not found")
        return GetCommentResponse.from_model(comment)

    @comments_router.get(
        "/comments",
        response_model=GetCommentsResponse,
        description="Returns a selection of comments by post"
    )
    @inject
    async def get_comments(
        self,
        payload: GetCommentsRequest = Depends(),
        account: Account = Scopes(ScopeEnum.COMMENTS_GET),
        db_session: Callable = Depends(Provide[Container.db_session]),
    ) -> GetCommentsResponse:
        async with db_session() as tx:
            post = await self._posts_service.get_post(tx, payload.post_id)
            if not post:
                raise LogicError(f"Post not found")
            
            if payload.owner_hex_id is not None:
                comments_owner = await self._accounts_service.get_account(
                    tx, account_hex_id=payload.owner_hex_id
                )
                if comments_owner is None:
                    raise LogicError("Invalid owner id")
                
            comments = await self._comments_service.get_comments(tx, payload)
        return GetCommentsResponse(
            comments = [
                GetCommentResponse.from_model(comment) for comment in comments
            ]
        )
    
    @comments_router.get(
        "/comments-daily-breakdown",
        response_model=GetCommentsBreakdownResponse,
        description="Returns a amount of comments by days"
    )
    @inject
    async def get_comments_daily_breakdown(
        self,
        payload: GetCommentsBreakdownRequest = Depends(),
        account: Account = Scopes(ScopeEnum.STATISTICS_GET),
        db_session: Callable = Depends(Provide[Container.db_session]),
    ) -> GetCommentsBreakdownResponse:
        async with db_session() as tx:
                
            breakdown = await self._comments_service.get_comments_breakdown(
                tx, payload
            )
        return GetCommentsBreakdownResponse(
            report = {
                row["date"].strftime("%Y-%m-%d") : DailyBreakdown(
                    created=row["created"],
                    blocked=row["blocked"]
                ) for row in breakdown
            }
        )

    @comments_router.put(
        "/comment",
        response_model=GetCommentResponse,
        description="Updates a comment by id"
    )
    @inject
    async def update_comment(
        self,
        payload: UpdateCommentRequest,
        account: Account = Scopes(ScopeEnum.COMMENTS_UPDATE),
        db_session: Callable = Depends(Provide[Container.db_session]),
    ) -> GetCommentResponse:
        async with db_session() as tx:
            comment = await self._comments_service.get_comment(
                tx,
                payload.comment_id
            )
            if comment is None:
                raise LogicError(f"Comment not found")
            comment.text = payload.text
        return GetCommentResponse.from_model(comment)
    
    @comments_router.delete(
        "/comment/{comment_id}",
        response_model=DeleteCommentResponse,
        description="Delete a comment by id"
    )
    @inject
    async def delete_comment(
        self,
        comment_id: int = Path(
            ..., 
            title="Unique id that corresponds to comment."
        ),
        account: Account = Scopes(ScopeEnum.COMMENTS_DELETE),
        db_session: Callable = Depends(Provide[Container.db_session]),
    ) -> GetCommentResponse:
        async with db_session() as tx:
            comment = await self._comments_service.get_comment(
                tx, comment_id, account.hex_id
            )
            if comment is not None:
                await self._comments_service.delete_comment(tx, comment)
                return DeleteCommentResponse(status="Ok")
        raise LogicError(f"Comment not found")

container.wire(modules=[__name__])
