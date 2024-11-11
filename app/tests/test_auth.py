import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from app.components.accounts.models import Account
from app.components.auth.consts import RoleEnum
from app.tests.base import AuthAPI, TestMixin
from app.tests.consts import PASSWORD
from app.tests.fixtures import f


@pytest.mark.asyncio
class TestAuth(TestMixin):
    async def test_accounts_api(
        self,
        f_session: AsyncSession,
        f_account: Account
    ) -> None:
        await f_session.refresh(f_account)
        api = AuthAPI(token=self.token)

        # validate token creation
        resp = await api.create(
            username=f_account.login, 
            password=PASSWORD
        )
        assert isinstance(resp.get("access_token"), str), resp
        assert resp.get("role") == RoleEnum.USER.value, resp
