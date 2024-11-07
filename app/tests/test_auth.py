import pytest

from app.components.auth.consts import RoleEnum
from app.tests.base import ApiRequests, TestMixin
from app.tests.consts import PASSWORD
from app.tests.fixtures import f


class AuthAPI(ApiRequests):
    API_ENDPOINT: str = "/api/v1/auth/token"


@pytest.mark.asyncio
class TestAuth(TestMixin):
    async def test_accounts_api(self, f_session, f_account):
        await f_session.refresh(f_account)
        api = AuthAPI(token=self.token)
        print(f_account.login)
        ###############################
        #  validate token creation  #
        
        resp = await api.create(
            username=f_account.login, 
            password=PASSWORD
        )
        assert isinstance(resp.get("access_token"), str), resp
        assert resp.get("role") == RoleEnum.USER.value, resp
