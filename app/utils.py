from contextlib import asynccontextmanager
from dependency_injector.wiring import inject, Provide
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from app.components.accounts.endpoints import accounts_router
from app.components.auth.endpoints import auth_router
from app.components.posts.endpoints import posts_router
from app.components.comments.endpoints import comments_router
from app.components.base.models import Base
from app.configs import AppConfig
from app.containers import container, Container
from app.database import DB
from app.exceptions import LogicError


@inject
def setup_app(
    config: AppConfig = Provide[Container.config],
    db: DB = Provide[Container.db],
    
):
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        
        engine = create_engine(config.db.master_sync)
        SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )
        Base.metadata.create_all(bind=engine)
        
        await db.init_db()
        yield
        await db.dispose()

    app = FastAPI(debug=config.env.debug, lifespan=lifespan)
    api_v1 = FastAPI(debug=config.env.debug)
    api_v1.include_router(accounts_router)
    api_v1.include_router(auth_router)
    api_v1.include_router(posts_router)
    api_v1.include_router(comments_router)
    app.mount("/api/v1", api_v1)

    if config.env.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @api_v1.exception_handler(Exception)
    async def debug_exception_handler(
        _: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(exc)
        return JSONResponse({
            "error": "Internal server error"},
            status_code=500
        )

    @api_v1.exception_handler(LogicError)
    async def validation_exception_handler(
        _: Request, exc: LogicError
    ) -> JSONResponse:
        logger.exception(exc)
        return JSONResponse({"error": str(exc)}, status_code=400)

    return app

container.wire(modules=[__name__])
