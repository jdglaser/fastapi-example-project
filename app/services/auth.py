from datetime import datetime, timedelta
from typing import Callable, Mapping, Optional

from fastapi import Depends, Response, Request
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from fastapi.security.utils import get_authorization_scheme_param
from passlib.context import CryptContext
from starlette import status
from jose import JWTError, ExpiredSignatureError, jwt

from app.database.database import get_repo
from app.database.repos.user_repo import UserRepo
from app.models.token import Token
from app.services.base_service import BaseService
from app.config import settings
import secrets

from app.services.token import TokenService

class AuthService(BaseService):
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

    def __init__(
        self,
        user_repo: UserRepo = Depends(get_repo(UserRepo))
    ) -> None:
        self.user_repo = user_repo
    
    @classmethod
    def create_token(cls, data: dict, expires_minutes: int) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.hashing_algorithm)
        return encoded_jwt

    @classmethod
    def parse_expired_token_from_header(
        cls,
        request: Request
    ) -> Mapping:
        authorization: str = request.headers.get("Authorization")
        _, credentials = get_authorization_scheme_param(authorization)
        try:
            payload = jwt.decode(
                credentials, 
                settings.secret_key, 
                algorithms=settings.hashing_algorithm,
                options={
                    "require_sub": True,
                    "verify_exp": False
                }
            )
            return payload
        except JWTError:
            raise cls.invalid_token_exception
    
    async def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)
        
    async def get_password_hash(self, password):
        return self.pwd_context.hash(password)
    
    async def login(
        self,
        response: Response, 
        username: str, 
        password: str
    ) -> Token:
        user = await self.user_repo.get_auth_user(username)
        await self.verify_password(password, user.hashed_password)

        refresh_token_expires_at = datetime.utcnow() + timedelta(minutes=settings.refresh_token_expire_minutes)

        access_token = self.create_token(
            data={"sub": user.username}, 
            expires_minutes=settings.access_token_expire_minutes
        )

        refresh_token = secrets.token_urlsafe(32)

        await self.user_repo.update_user_refresh_token(username, refresh_token, refresh_token_expires_at)

        response.delete_cookie("refresh_token")
        response.set_cookie("refresh_token", 
                            refresh_token, 
                            httponly=True,
                            samesite="strict",
                            secure=True,
                            path="/auth/refresh")
        return Token(access_token=access_token, token_type="bearer")

    
    async def refresh_access_token(
        self,
        request: Request
    ) -> Token:
        invalid_refresh_token_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token")
        refresh_token: Optional[str] = request.cookies.get("refresh_token")
        if not refresh_token:
            raise invalid_refresh_token_exception

        token = self.parse_expired_token_from_header(request)
        username = token.get("sub")
        print(token)

        if not username:
            raise self.invalid_token_exception

        refresh_token_for_user, refresh_token_for_user_expires_at = await self.user_repo.get_user_refresh_token(username)

        if (refresh_token_for_user is None or refresh_token_for_user_expires_at is None):
            raise invalid_refresh_token_exception

        if (refresh_token_for_user != refresh_token):
            raise invalid_refresh_token_exception
        
        if (datetime.utcnow() > refresh_token_for_user_expires_at):
            raise invalid_refresh_token_exception
        
        access_token = self.create_token(
            data={"sub": username}, 
            expires_minutes=settings.access_token_expire_minutes
        )

        return Token(access_token=access_token, token_type="bearer")

    