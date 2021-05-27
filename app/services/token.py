from datetime import datetime, timedelta
from fastapi.exceptions import HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials
from jose import JWTError, ExpiredSignatureError, jwt
from sqlalchemy import schema
from app.config import settings
from fastapi.security import HTTPBearer
from typing import Mapping, Optional
from fastapi import status, Depends, Request
from passlib.context import CryptContext


class TokenService():
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    invalid_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    scheme = HTTPBearer()

    def __init__(
        self,
        token: Optional[HTTPAuthorizationCredentials] = Depends(scheme)
    ) -> None:
        self.token = token


    async def get_refresh_token_from_header(self, request: Request) -> str:
        token: Optional[str] = request.cookies.get("refresh_token")
        if not token:
            raise self.invalid_token_exception
        return token

    async def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)
        
    async def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def create_token(self, data: dict, expires_minutes: int) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.hashing_algorithm)
        return encoded_jwt

    def verify_token(self, token, verify_expiration = True) -> Mapping:
        try:
            payload = jwt.decode(
                token, 
                settings.secret_key, 
                algorithms=settings.hashing_algorithm,
                options={
                    "require_sub": True,
                    "verify_exp": verify_expiration
                }
            )
            return payload
        except ExpiredSignatureError:
            raise self.token_expired_exception
        except JWTError:
            raise self.invalid_token_exception

    def get_current_user(
        self,
        verify_expiration = True
    ) -> str:
        if not self.token:
            raise self.invalid_token_exception
        payload = self.verify_token(self.token.credentials, verify_expiration=verify_expiration)
        username: Optional[str] = payload.get("sub")
        if not username:
            raise self.invalid_token_exception
        return username

    def get_current_expired_user(
        self
    ) -> str:
        return self.get_current_user(verify_expiration=False)