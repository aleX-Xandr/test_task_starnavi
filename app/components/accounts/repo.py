from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional

from app.components.accounts.exceptions import AccountEntityAlreadyExist
from app.components.accounts.models import Account


class AccountRepository:
    @staticmethod
    async def add_account(tx: AsyncSession, account: Account) -> Account:
        tx.add(account)
        try:
            await tx.flush()
        except IntegrityError:
            raise AccountEntityAlreadyExist(account.login)
        await tx.commit()
        await tx.refresh(account)
        return account
    
    @staticmethod
    async def get_account_by_id(
        tx: AsyncSession, account_id: Optional[int] = None, account_hex_id: Optional[str] = None
    ) -> Account | None:
        q = select(Account)
        if account_id:
            q = q.where(Account.id == account_id)
        if account_hex_id:
            q = q.where(Account.hex_id == account_hex_id)
        raw = await tx.execute(q)
        return raw.scalar_one_or_none()

