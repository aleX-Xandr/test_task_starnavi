import pytest
import random

from datetime import datetime, timezone, timedelta
from http import HTTPStatus

from app.tests.base import ApiRequests, TestMixin
from app.tests.consts import ContentTypeEnum
from app.tests.fixtures import f


class CommentAPI(ApiRequests):
    API_ENDPOINT: str = "/api/v1/comment"


@pytest.mark.asyncio
class TestComment(TestMixin):
    async def test_comment_api(self, f_session, f_post, f_comment):
        await f_session.refresh(f_post)
        await f_session.refresh(f_comment)

        api = CommentAPI(token=self.token)
        text = f.paragraph(nb_sentences=random.randint(3, 7))

        # create comment
        comment = await api.create(
            text=text, post_id=f_post.id, content_type=ContentTypeEnum.JSON
        )
        assert comment.get("text") == text, comment
        comment_id = comment.get("id")

        # get comment
        get_comment = await api.get(comment_id=comment_id)
        assert get_comment.get("id") == comment_id, get_comment

        # # get all comments
        resp = await api.get(endpoint=f"/api/v1/comments", post_id=f_post.id)
        comments = resp.get("comments", None)
        assert isinstance(comments, list), resp
        assert len(comments) > 0, resp

        # update comment
        new_text = f.paragraph(nb_sentences=random.randint(3, 7))
        new_comment = await api.update(comment_id=comment_id, text=new_text)
        assert new_comment.get("id") == comment_id, new_comment
        assert new_comment.get("text") == new_text, new_comment

        # get comment daily breakdown
        date_to = datetime.now(timezone.utc)
        date_from = date_to - timedelta(days = 3)
        breakdown = await api.get(
            endpoint=f"/api/v1/comments-daily-breakdown",
            date_from=date_from.strftime("%Y-%m-%d"),
            date_to = date_to.strftime("%Y-%m-%d")
        )
        report = breakdown.get("report")
        assert isinstance(report, dict), breakdown
        assert len(report) > 0, breakdown

        # delete comment
        del_comment = await api.delete(
            endpoint=f"/api/v1/comment/{comment_id}"
        )
        assert del_comment.get("status") == "Ok", del_comment

        # get deleted comment
        get_comment = await api.get(
            comment_id=comment_id,
            expected_status_code=HTTPStatus.BAD_REQUEST
        )
        assert get_comment.get("error") == "Comment not found", get_comment

        # update deleted comment
        new_text = f.paragraph(nb_sentences=random.randint(3, 7))
        new_comment = await api.update(
            comment_id=comment_id, 
            text=new_text,
            expected_status_code=HTTPStatus.BAD_REQUEST
        )
        assert new_comment.get("error") == "Comment not found", new_comment

        # delete deleted comment
        del_comment = await api.delete(
            endpoint=f"/api/v1/comment/{comment_id}",
            expected_status_code=HTTPStatus.BAD_REQUEST
        )
        assert del_comment.get("error") == "Comment not found", del_comment

        
