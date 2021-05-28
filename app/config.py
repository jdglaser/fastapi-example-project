import logging

from pydantic import BaseSettings


class Settings(BaseSettings):
    '''Pydantic settings class
    All settings can be overridden by env variables.
    Pydantic will look for an all caps version of the setting name.
    e.g. setting `foo` will match to env variable `FOO`
    '''
    # Project settings
    project_name: str = "Example FastAPI Project"
    project_version: str = "1.0"
    log_level: int = logging.DEBUG
    allowed_origins: list[str] = ["http://localhost:3000"]
    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_username: str = "postgres"
    db_password: str = "postgres"
    db_name: str = "postgres"
    db_min_connection_pool_size: int = 5
    db_max_connection_pool_size: int = 20
    # Auth
    hashing_algorithm: str = "HS256"
    secret_key: str = "super_secret_key"
    access_token_expire_minutes: int = 1
    refresh_token_expire_minutes: int = 2

settings = Settings(_env_file=None)
