import secrets
from datetime import datetime, timedelta
from src.models.user import AuthUserTemplate, UserTemplate
from src.util.logging import get_logger
from typing import Mapping, Optional

from src.config import settings
from src.database.repos.user_repo import UserRepo
from src.models.token import Token
from fastapi import Depends, Request, Response
from fastapi.exceptions import HTTPException
from src.util.http_bearer import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from starlette import status

logger = get_logger(__name__)

class AuthService():
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    auth_scheme = HTTPBearer()

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
        user_repo: UserRepo = Depends()
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
        token: Optional[HTTPAuthorizationCredentials] = Depends(auth_scheme)
    ) -> Mapping:
        if not token:
            raise cls.invalid_token_exception
        try:
            payload = jwt.decode(
                token.credentials, 
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
    
    @classmethod
    def verify_token(cls, token) -> Mapping:
        try:
            payload = jwt.decode(
                token, 
                settings.secret_key, 
                algorithms=settings.hashing_algorithm,
                options={
                    "require_sub": True,
                    "verify_exp": True
                }
            )
            return payload
        except ExpiredSignatureError:
            raise cls.token_expired_exception
        except JWTError:
            raise cls.invalid_token_exception
    
    @classmethod
    def verify_current_user(
        cls,
        token: Optional[HTTPAuthorizationCredentials] = Depends(auth_scheme)
    ) -> str:
        if not token:
            raise cls.invalid_token_exception
        payload = cls.verify_token(token.credentials)
        username: Optional[str] = payload.get("sub")
        logger.info(f"USERNAME: {username}")
        if not username:
            raise AuthService.invalid_token_exception
        return username
    
    async def verify_password(self, plain_password, hashed_password) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
        
    async def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    async def register_user(self, user: UserTemplate):
        hashed_password = await self.get_password_hash(user.password)
        auth_user = AuthUserTemplate(hashed_password=hashed_password,
                                     **dict(user))
        user_in_db = await self.user_repo.find_user(user.username)
        user_email_in_db = await self.user_repo.find_user_by_email(user.email)
        if user_in_db:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A user with the name {user.username} already exists."
            )
        if user_email_in_db:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A user with the email {user.email} already exists."
            )
        return await self.user_repo.create_user(auth_user)
    
    async def login(
        self,
        response: Response, 
        username: str, 
        password: str
    ) -> Token:
        user = await self.user_repo.get_auth_user(username)
        password_verified = await self.verify_password(password, user.hashed_password)
        if (not password_verified):
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail=f"Login failed for user {username}"
            )

        refresh_token_expires_at = datetime.utcnow() + timedelta(minutes=settings.refresh_token_expire_minutes)

        access_token = self.create_token(
            data={"sub": user.username}, 
            expires_minutes=settings.access_token_expire_minutes
        )

        refresh_token = secrets.token_urlsafe(32)

        logger.info("updating refresh token")
        await self.user_repo.update_user_refresh_token(username, refresh_token, refresh_token_expires_at)

        response.delete_cookie("refresh_token")
        response.set_cookie("refresh_token", 
                            refresh_token, 
                            httponly=True,
                            samesite="none",
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
        logger.info(refresh_token)
        if not refresh_token:
            raise invalid_refresh_token_exception

        user = await self.user_repo.find_user_by_refresh_token(refresh_token)
        logger.info(f"user: {user}")

        if not user:
            raise self.invalid_token_exception

        refresh_token_for_user, refresh_token_for_user_expires_at = await self.user_repo.get_user_refresh_token(user.username)

        if (refresh_token_for_user is None or refresh_token_for_user_expires_at is None):
            raise invalid_refresh_token_exception

        if (refresh_token_for_user != refresh_token):
            raise invalid_refresh_token_exception
        
        if (datetime.utcnow() > refresh_token_for_user_expires_at):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Expired refresh token")
        
        access_token = self.create_token(
            data={"sub": user.username}, 
            expires_minutes=settings.access_token_expire_minutes
        )

        return Token(access_token=access_token, token_type="bearer")

    