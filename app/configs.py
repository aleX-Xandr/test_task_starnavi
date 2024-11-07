from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings

import os

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL") #type: ignore

settings = Settings()


class AuthConfig(BaseModel):
    secret_key: str
    algorithm: str
    token_expiration_minutes: float


class DbConfig(BaseModel):
    master: str
    master_pool_min_size: int
    master_pool_max_size: int


class EnvConfig(BaseModel):
    port: int
    enable_cors: bool
    debug: bool


class AppConfig(BaseModel):
    env: EnvConfig
    db: DbConfig
    auth: AuthConfig
