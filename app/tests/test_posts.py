import pytest
import random

from http import HTTPStatus

from app.tests.base import ApiRequests, TestMixin
from app.tests.consts import ContentTypeEnum
from app.tests.fixtures import f


class PostsAPI(ApiRequests):
    API_ENDPOINT: str = "/api/v1/posts"


@pytest.mark.asyncio
class TestPosts(TestMixin):
    async def test_posts_api(self):
        api = PostsAPI(token=self.token)

        ##############################
        #  validate posts receiving  #
        
        resp = await api.get()
        posts = resp.get("posts", None)
        assert isinstance(posts, list), resp
        assert len(posts) > 0, resp
        
