from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession

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
        tx: AsyncSession, account_id: int
    ) -> Account | None:
        q = select(Account).where(Account.id == account_id)
        raw = await tx.execute(q)
        return raw.scalar_one_or_none()

