from http import HTTPStatus
from typing import Any, Dict, Optional, Literal

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
    headers: Dict

    def __init__(self, token: str):
        self.headers = {
            "Authorization": f"Bearer {token}"
        }

    async def call_api(
            self,
            method: str,
            expected_status_code: HTTPStatus = HTTPStatus.OK,
            extra_headers: Optional[Dict] = None,
            **kwargs
    ) -> Response:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as api_client:
            resp = await api_client.request(
                method=method,
                url=self.API_ENDPOINT,
                headers=self.headers,
                **kwargs
            )
            assert resp.status_code == expected_status_code, resp.content
            return resp

    async def request(
        self, 
        method: Literal["GET", "POST", "PUT", "DELETE"],
        expected_status_code: HTTPStatus, 
        content_type: ContentTypeEnum,
        endpoint: Optional[str] = None,
        **kwargs
    ) -> Any:
        data = json = params = None

        if content_type == ContentTypeEnum.FORM:
            data = kwargs
        elif content_type == ContentTypeEnum.JSON:
            json = kwargs
        else: # ContentTypeEnum.QUERY
            params = kwargs

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver", timeout=30) as api_client:
            resp = await api_client.request(
                method=method,
                url=endpoint or self.API_ENDPOINT,
                headers=self.headers,
                params=params,
                data=data,
                json=json,
            )
            assert resp.status_code == expected_status_code, resp.content
            return resp.json()

    async def create(
        self, 
        endpoint: Optional[str] = None,
        expected_status_code: HTTPStatus = HTTPStatus.OK, 
        content_type: ContentTypeEnum = ContentTypeEnum.FORM,
        **kwargs
    ) -> Any:
        return await self.request(
            "POST",
            expected_status_code,
            content_type,
            endpoint,
            **kwargs
        )
        
    async def get(
        self, 
        endpoint: Optional[str] = None,
        expected_status_code: HTTPStatus = HTTPStatus.OK, 
        content_type: ContentTypeEnum = ContentTypeEnum.QUERY,
        **kwargs
    ) -> Any:
        return await self.request(
            "GET",
            expected_status_code,
            content_type,
            endpoint,
            **kwargs
        )
        
    async def update(
        self, 
        endpoint: Optional[str] = None,
        expected_status_code: HTTPStatus = HTTPStatus.OK, 
        content_type: ContentTypeEnum = ContentTypeEnum.JSON,
        **kwargs
    ) -> Any:
        return await self.request(
            "PUT",
            expected_status_code,
            content_type,
            endpoint,
            **kwargs
        )
        
    async def delete(
        self, 
        endpoint: Optional[str] = None,
        expected_status_code: HTTPStatus = HTTPStatus.OK, 
        content_type: ContentTypeEnum = ContentTypeEnum.QUERY,
        **kwargs
    ) -> Any:
        return await self.request(
            "DELETE",
            expected_status_code,
            content_type,
            endpoint,
            **kwargs
        )


class AccountsAPI(ApiRequests):
    API_ENDPOINT: str = "/api/v1/accounts/register"


class AuthAPI(ApiRequests):
    API_ENDPOINT: str = "/api/v1/auth/token"


class CommentAPI(ApiRequests):
    API_ENDPOINT: str = "/api/v1/comment"


class PostAPI(ApiRequests):
    API_ENDPOINT: str = "/api/v1/post"
