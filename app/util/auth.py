from typing import Optional

from app.config import settings
from app.util.jwt_auth import JWTAuth
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from starlette.requests import Request

token_bearer_scheme = HTTPBearer()

jwt_auth = JWTAuth(secret_key=settings.secret_key, 
                   algorithm=settings.hashing_algorithm,
                   pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto"))

async def get_refresh_token_from_header(request: Request) -> str:
    token: Optional[str] = request.cookies.get("refresh_token")
    if not token:
        raise jwt_auth.invalid_token_exception
    return token

def verify_current_user(token: Optional[HTTPAuthorizationCredentials] = Depends(token_bearer_scheme)) -> str:
    payload = jwt_auth.verify_token(token.credentials)
    username: str = payload.get("sub")
    return username

def retrieve_current_user(token: Optional[HTTPAuthorizationCredentials] = Depends(token_bearer_scheme)) -> str:
    payload = jwt_auth.decode_token_without_exp_verification(token.credentials)
    username: str = payload.get("sub")
    return username
