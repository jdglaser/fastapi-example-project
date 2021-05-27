import logging

from pydantic import BaseSettings


class Settings(BaseSettings):
    project_name: str = "Example FastAPI Project"
    project_version: str = "1.0"
    log_level: int = logging.DEBUG
    allowed_origins: list[str] = ["http://localhost:3000"]
    db_host: str = "localhost"
    db_port: int = 5432
    db_username: str = "postgres"
    db_password: str = "postgres"
    db_name: str = "postgres"
    db_min_connection_pool_size: int = 5
    db_max_connection_pool_size: int = 20
    hashing_algorithm: str = "HS256"
    secret_key: str = "super_secret_key"
    access_token_expire_minutes: int = 1
    refresh_token_expire_minutes: int = 30

settings = Settings(_env_file=None)
