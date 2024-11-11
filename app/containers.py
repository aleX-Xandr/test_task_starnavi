from dependency_injector import containers, providers
from passlib.context import CryptContext
from pyaml_env import parse_config

from app.components.accounts.repo import AccountRepository
from app.components.accounts.service import AccountService
from app.components.auth.repo import AuthRepository
from app.components.auth.service import AuthService
from app.components.comments.repo import CommentRepository
from app.components.comments.service import CommentService
from app.components.gemini.service import GeminiService
from app.components.posts.repo import PostRepository
from app.components.posts.service import PostService
from app.configs import AppConfig
from app.constants import CONFIG_FILE
from app.database import DB


class Container(containers.DeclarativeContainer):
    config: providers.Provider = providers.Singleton(
        AppConfig, **parse_config(CONFIG_FILE)
    )

    db: providers.Provider = providers.Singleton(
        DB, config=config.provided.db, debug=config.provided.env.debug
    )
    db_session: providers.Provider = providers.Factory(
        db.provided.get_session
    )

    crypt_context: providers.Provider = providers.Singleton(
        CryptContext, schemes=["bcrypt"], deprecated="auto"
    )

    accounts_repository: providers.Provider = providers.Singleton(
        AccountRepository
    )
    accounts_service: providers.Provider = providers.Singleton(
        AccountService,
        accounts_repository=accounts_repository,
    )

    auth_repository: providers.Provider = providers.Singleton(AuthRepository)
    auth_service: providers.Provider = providers.Singleton(
        AuthService,
        config=config.provided.auth,
        auth_repository=auth_repository,
        crypt_context=crypt_context,
    )

    comments_repository: providers.Provider = providers.Singleton(
        CommentRepository
    )
    comments_service: providers.Provider = providers.Singleton(
        CommentService,
        comments_repository=comments_repository,
    )

    gemini_service: providers.Provider = providers.Singleton(
        GeminiService,
        config=config.provided.gemini
    )

    posts_repository: providers.Provider = providers.Singleton(PostRepository)
    posts_service: providers.Provider = providers.Singleton(
        PostService,
        posts_repository=posts_repository,
    )

container = Container()
