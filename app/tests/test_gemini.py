import pytest
import asyncio

from http import HTTPStatus
from sqlalchemy.ext.asyncio import AsyncSession

from app.components.posts.models import Post
from app.tests.base import CommentAPI, TestMixin
from app.tests.consts import ContentTypeEnum, TEXT, BAD_TEXT
from app.tests.fixtures import f


@pytest.mark.asyncio
class TestAutoComment(TestMixin):
    async def test_auto_comment(
        self,
        f_session: AsyncSession,
        f_post_auto_reply: Post
    ) -> None:
        await f_session.refresh(f_post_auto_reply)

        api = CommentAPI(token=self.token)

        # create comment
        comment = await api.create(
            text=TEXT, 
            post_id=f_post_auto_reply.id, 
            content_type=ContentTypeEnum.JSON
        )
        assert comment.get("text") == TEXT, comment
        comment_id = comment.get("id")

        # get all comments
        resp = await api.get(
            endpoint=f"/api/v1/comments", 
            post_id=f_post_auto_reply.id
        )
        comments = resp.get("comments", None)
        assert isinstance(comments, list), resp
        assert len(comments) == 1, resp

        # get all comments after auto reply 
        max_attempts = 3
        delay = 20
        for _ in range(max_attempts):
            resp = await api.get(
                endpoint=f"/api/v1/comments", 
                post_id=f_post_auto_reply.id
            )
            comments = resp.get("comments", None)
            if isinstance(comments, list) and len(comments) == 2:
                break
            await asyncio.sleep(delay)
        else:
            raise AssertionError("Фоновое задание не завершилось вовремя.")

        # create bad comment
        comment = await api.create(
            text=BAD_TEXT, 
            post_id=f_post_auto_reply.id, 
            content_type=ContentTypeEnum.JSON,
            expected_status_code=HTTPStatus.BAD_REQUEST
        )
        assert comment.get("error") == "Comment was banned!", comment
        
        # get all comments after create bad comment
        resp = await api.get(
            endpoint=f"/api/v1/comments", 
            post_id=f_post_auto_reply.id
        )
        comments = resp.get("comments", None)
        assert isinstance(comments, list), resp
        assert len(comments) == 2, resp

        # update good comment to make it bad
        new_comment = await api.update(
            comment_id=comment_id, 
            text=BAD_TEXT,
            expected_status_code=HTTPStatus.BAD_REQUEST
        )
        assert new_comment.get("error") == "Comment was banned!", comment
        
        # get all comments after modify good comment
        resp = await api.get(
            endpoint=f"/api/v1/comments", 
            post_id=f_post_auto_reply.id
        )
        comments = resp.get("comments", None)
        assert isinstance(comments, list), resp
        assert len(comments) == 1, resp
