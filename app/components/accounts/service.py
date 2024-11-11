from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional

from app.components.accounts.models import Account
from app.components.accounts.repo import AccountRepository


class AccountService:
    def __init__(self, accounts_repository: AccountRepository):
        self._accounts_repository = accounts_repository

    async def add_account(
        self,
        tx: AsyncSession,
        account: Account
    ) -> Account:
        return await self._accounts_repository.add_account(tx, account)

    async def get_account(
        self,
        tx: AsyncSession,
        account_id: Optional[int] = None,
        account_hex_id: Optional[str] = None
    ) -> Account | None:
        if account_id is None and account_hex_id is None:
            return None
        
        return await self._accounts_repository.get_account(
            tx, account_id, account_hex_id
        )
