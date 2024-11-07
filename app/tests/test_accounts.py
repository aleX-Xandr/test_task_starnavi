import pytest

from http import HTTPStatus

from app.tests.base import ApiRequests, TestMixin
from app.tests.consts import PASSWORD
from app.tests.fixtures import f


class AccountsAPI(ApiRequests):
    API_ENDPOINT: str = "/api/v1/accounts/register"


@pytest.mark.asyncio
class TestAccounts(TestMixin):
    async def test_accounts_api(self):
        login = f.pystr(min_chars=5, max_chars=20)

        api = AccountsAPI(token=self.token)

        ###############################
        #  validate account creation  #
        
        resp = await api.create(username=login, password=PASSWORD)
        assert resp.get("created"), resp
        
        resp = await api.create(expected_status_code=HTTPStatus.BAD_REQUEST, username=login, password=PASSWORD)
        assert resp.get("error") == f"Account already exists: {login}", resp
