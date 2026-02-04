from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, field_validator
from pydantic import PostgresDsn, KafkaDsn
from pathlib import Path
from enum import StrEnum


BASE_DIR = Path(__file__).parent.parent.parent


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8008


class TransportConfig(BaseModel):
    kafka_url: KafkaDsn


class AuthConfig(BaseModel): ...


class JwtAuthConfig(AuthConfig):
    public_key: Path = BASE_DIR / "certificates" / "jwt-public.pem"
    algorithm: str

    @field_validator("algorithm")
    def validate_algorithm(cls, value: str) -> str:
        allowed: list[str] = [
            "RS256",
            "RS2048",
        ]

        if value in allowed:
            return value
        else:
            raise ValueError(
                f"""Current algorithm "{value}" is not allowed. Allowed: f{", ".join(allowed)}"""
            )


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env_app",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    db: DatabaseConfig
    transport: TransportConfig
    auth: JwtAuthConfig


settings = Settings()
