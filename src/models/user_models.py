from datetime import date, datetime
from typing import Optional

from src.models.main_model import MainModel


class User(MainModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: Optional[str]
    date_of_birth: date
    disabled: bool

class AuthUser(User):
    hashed_password: str
    refresh_token: Optional[str]
    refresh_token_expires_at: Optional[datetime]

class UserTemplate(MainModel):
    username: str
    email: str
    first_name: str
    last_name: Optional[str]
    date_of_birth: date
    password: str

class AuthUserTemplate(UserTemplate):
    hashed_password: str
