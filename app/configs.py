from pydantic import BaseModel


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


class GenerationConfig(BaseModel):
    temperature: float
    top_p: float
    top_k: int
    max_output_tokens: int
    response_mime_type: str


class GeminiConfig(BaseModel):
    api_key: str
    generation_config: GenerationConfig


class AppConfig(BaseModel):
    env: EnvConfig
    db: DbConfig
    auth: AuthConfig
    gemini: GeminiConfig
