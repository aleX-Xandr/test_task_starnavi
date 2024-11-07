from fastapi import FastAPI
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.configs import settings
from app.components.base.models import Base
from app.components.accounts.endpoints import accounts_router
from app.components.auth.endpoints import auth_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(accounts_router)
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
