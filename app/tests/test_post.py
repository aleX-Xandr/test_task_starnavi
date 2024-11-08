import pytest
import random

from http import HTTPStatus

from app.tests.base import ApiRequests, TestMixin
from app.tests.consts import ContentTypeEnum
from app.tests.fixtures import f


class PostAPI(ApiRequests):
    API_ENDPOINT: str = "/api/v1/post"


@pytest.mark.asyncio
class TestPost(TestMixin):
    async def test_post_api(self):
        text = f.paragraph(nb_sentences=random.randint(3, 7))

        api = PostAPI(token=self.token)
        
        # create post
        post = await api.create(text=text, content_type=ContentTypeEnum.JSON)
        assert post.get("text") == text, post
        post_id = post.get("id")

        # get post
        get_post = await api.get(post_id=post_id)
        assert get_post.get("id") == post_id, get_post

        # get all posts
        resp = await api.get(endpoint=f"/api/v1/posts")
        posts = resp.get("posts", None)
        assert isinstance(posts, list), resp
        assert len(posts) > 0, resp

        # update post
        new_text = f.paragraph(nb_sentences=random.randint(3, 7))
        new_post = await api.update(post_id=post_id, text=new_text)
        assert new_post.get("id") == post_id, new_post
        assert new_post.get("text") == new_text, new_post

        # delete post
        del_post = await api.delete(endpoint=f"/api/v1/post/{post_id}")
        assert del_post.get("status") == "Ok", del_post

        # get deleted post
        get_post = await api.get(
            post_id=post_id,
            expected_status_code=HTTPStatus.BAD_REQUEST
        )
        assert get_post.get("error") == "Post not found", get_post

        # update deleted post
        new_text = f.paragraph(nb_sentences=random.randint(3, 7))
        new_post = await api.update(
            post_id=post_id, 
            text=new_text,
            expected_status_code=HTTPStatus.BAD_REQUEST
        )
        assert new_post.get("error") == "Post not found", new_post

        # delete deleted post
        del_post = await api.delete(
            endpoint=f"/api/v1/post/{post_id}",
            expected_status_code=HTTPStatus.BAD_REQUEST
        )
        assert del_post.get("error") == "Post not found", del_post
