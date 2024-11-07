import pytest
import random

from http import HTTPStatus

from app.tests.base import ApiRequests, TestMixin
from app.tests.consts import ContentTypeEnum
from app.tests.fixtures import f


class PostsAPI(ApiRequests):
    API_ENDPOINT: str = "/api/v1/posts/create"


@pytest.mark.asyncio
class TestPosts(TestMixin):
    async def test_accounts_api(self):
        text = f.paragraph(nb_sentences=random.randint(3, 7))

        api = PostsAPI(token=self.token)

        ############################
        #  validate post creation  #
        
        resp = await api.create(text=text, content_type=ContentTypeEnum.JSON)
        assert resp.get("text") == text, resp
        
