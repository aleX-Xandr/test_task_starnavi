from http import HTTPStatus
from typing import Any, Dict, Optional

from httpx import AsyncClient, ASGITransport, Response
from pytest_asyncio import fixture

from app.main import app
from app.tests.consts import ContentTypeEnum


class TestMixin:
    token: str
    API_VERSION = "api/v1"
    TOKEN_API = f"{API_VERSION}/auth/token"

    @fixture(autouse=True)
    async def init_token(self, f_session, f_auth):
        self.token = await self._get_token(f_auth.login)

    async def _get_token(self, login):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as api_client:
            resp = await api_client.post(
                self.TOKEN_API,
                data={
                    "username": login,
                    "password": "test_pass",
                }
            )
            assert resp.status_code == HTTPStatus.OK, resp.content
            resp_jsn = resp.json()

            token = resp_jsn.get("access_token")
            assert token is not None

            return token


class ApiRequests:
    API_ENDPOINT: str

    def __init__(self, token: str):
        self.token = token

    async def call_api(
            self,
            method: str,
            expected_status_code: HTTPStatus = HTTPStatus.OK,
            url_path: Optional[str] = None,
            extra_headers: Optional[dict] = None,
            **kwargs
    ) -> Response:
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        if extra_headers:
            headers.update(extra_headers)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as api_client:
            resp = await api_client.request(
                method=method,
                url=url_path or self.API_ENDPOINT,
                headers=headers,
                **kwargs
            )
            assert resp.status_code == expected_status_code, resp.content
            return resp

    async def create(
        self, 
        expected_status_code: HTTPStatus = HTTPStatus.OK, 
        content_type: ContentTypeEnum = ContentTypeEnum.FORM,
        **payload
    ) -> Dict[Any, Any]:

        if content_type == ContentTypeEnum.FORM:
            data = payload
            json = None
        else:
            data = None
            json = payload

        resp = await self.call_api(
            method="POST",
            data=data,
            json=json,
            expected_status_code=expected_status_code
        )
        json_data = resp.json()
        return json_data