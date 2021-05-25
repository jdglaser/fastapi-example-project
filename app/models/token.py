from typing import Optional

from app.models.main_model import MainModel


class Token(MainModel):
    access_token: str
    token_type: str


class TokenData(MainModel):
    username: Optional[str] = None
