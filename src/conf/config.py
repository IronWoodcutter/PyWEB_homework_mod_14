from typing import Any

from pydantic import ConfigDict, field_validator, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:567234@localhost:5432/contacts_rest_api"
    SECRET_KEY_JWT: str = "123"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: EmailStr = "admin@example.com"
    MAIL_PASSWORD: str = "admin"
    MAIL_FROM: str = "admin@example.com"
    MAIL_PORT: int = "34567"
    MAIL_SERVER: str = "localhost"
    REDIS_DOMAIN: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    CLD_NAME: str = "contacts_rest_api"
    CLD_API_KEY: int = 994257153597563
    CLD_API_SECRET: str = "secret"

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, value: Any):
        if value not in ["HS256", "HS512"]:
            raise ValueError("Invalid algorithm specified")
        return value


    model_config = ConfigDict(extra='ignore', env_file = ".env", env_file_encoding = "utf-8")  # noqa


config = Settings()

