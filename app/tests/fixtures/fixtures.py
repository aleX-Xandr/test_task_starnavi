import pytest_asyncio
import random
import secrets

from sqlalchemy.ext.asyncio import AsyncSession

from app.components.accounts.models import Account
from app.components.auth.consts import RolePermissionsEnum
from app.components.auth.models import Auth
from app.components.posts.models import Post
from app.containers import container
from app.tests.consts import PASSWORD
from app.tests.fixtures import f

@pytest_asyncio.fixture
async def f_account(f_session: AsyncSession) -> Account:
    account_ = Account(
        hex_id=secrets.token_hex(16),
        login=f.pystr(min_chars=5, max_chars=20)
    )
    f_session.add(account_)

    await f_session.commit()
    await f_session.refresh(account_)
    return account_

@pytest_asyncio.fixture
async def f_auth(f_session: AsyncSession, f_account: Account) -> Auth:
    hashed_pwd = container.crypt_context().hash(PASSWORD)
    auth_ = Auth(
        account_id=f_account.id,
        login=f_account.login,
        hashed_password=hashed_pwd,
        scopes=RolePermissionsEnum.ADMIN.value,
    )
    f_session.add(auth_)

    await f_session.commit()
    await f_session.refresh(auth_)
    return auth_

@pytest_asyncio.fixture
async def f_post(f_session: AsyncSession, f_account: Account) -> Post:
    await f_session.refresh(f_account)
    post_ = Post(
        account_hex_id=f_account.hex_id,
        text=f.paragraph(nb_sentences=random.randint(3, 7))
    )
    f_session.add(post_)

    await f_session.commit()
    await f_session.refresh(post_)
    return post_

@pytest_asyncio.fixture
async def f_post_auto_reply(
    f_session: AsyncSession,
    f_account: Account
) -> Post:
    await f_session.refresh(f_account)
    # Meaningful text is required for correct testing
    post_ = Post(
        account_hex_id=f_account.hex_id,
        text="Hello everyone, how is your day going?",
        auto_comment_timeout=5
    )
    f_session.add(post_)

    await f_session.commit()
    await f_session.refresh(post_)
    return post_
