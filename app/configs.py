from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class AuthConfig(BaseModel):
    secret_key: str
    algorithm: str
    token_expiration_minutes: float


class DbConfig(BaseModel):
    master: str
    master_sync: str
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
