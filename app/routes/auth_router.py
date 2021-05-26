import secrets
from datetime import datetime, timedelta
from typing import Optional

from app.config import settings
from app.database.repos.user_repo import UserRepo
from app.models.token import Token
from app.models.user import AuthUserTemplate, User, UserTemplate
from app.util.auth import jwt_auth, retrieve_current_user, verify_current_user
from app.util.logging import get_logger
from fastapi import (APIRouter, Depends, HTTPException, Request,
                     Response, status)
from fastapi.security import HTTPBearer
from app.database.database import get_repository
from app.models.token import Token

token_bearer_scheme = HTTPBearer()

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

LOG = get_logger(__name__)


@router.post("/login", response_model=Token)
async def login(response: Response, 
                username: str, 
                password: str,
                user_repo: UserRepo = Depends(get_repository(UserRepo))) -> Token:
    user = await user_repo.get_auth_user(username)
    jwt_auth.verify_password(password, user.hashed_password)

    refresh_token_expires_at = datetime.utcnow() + timedelta(minutes=settings.refresh_token_expire_minutes)

    access_token = await jwt_auth.create_token(
        data={"sub": user.username}, 
        expires_minutes=settings.access_token_expire_minutes
    )

    refresh_token = secrets.token_urlsafe(32)

    await user_repo.update_user_refresh_token(username, refresh_token, refresh_token_expires_at)

    response.delete_cookie("refresh_token")
    response.set_cookie("refresh_token", 
                        refresh_token, 
                        httponly=True,
                        samesite="strict",
                        secure=True,
                        path="/auth/refresh")
    return Token(access_token=access_token, token_type="bearer")

@router.post("/refresh", response_model=Token)
async def refresh_access_token(request: Request, 
                               username: str = Depends(retrieve_current_user),
                               user_repo: UserRepo = Depends(get_repository(UserRepo))) -> Token:
    invalid_refresh_token_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
    refresh_token: Optional[str] = request.cookies.get("refresh_token")
    if not refresh_token:
        raise invalid_refresh_token_exception
    
    refresh_token_for_user, refresh_token_for_user_expires_at = await user_repo.get_user_refresh_token(username)

    if (refresh_token_for_user is None or refresh_token_for_user_expires_at is None):
        raise invalid_refresh_token_exception

    if (refresh_token_for_user != refresh_token):
        raise invalid_refresh_token_exception
    
    if (datetime.utcnow() > refresh_token_for_user_expires_at):
        raise invalid_refresh_token_exception
    
    access_token = await jwt_auth.create_token(
        data={"sub": username}, 
        expires_minutes=settings.access_token_expire_minutes
    )

    return Token(access_token=access_token, token_type="bearer")

@router.post("/")
async def create_new_user(user: UserTemplate,
                          user_repo: UserRepo = Depends(get_repository(UserRepo))) -> User:
    hashed_password = await jwt_auth.get_password_hash(user.password)
    auth_user: AuthUserTemplate = AuthUserTemplate(hashed_password=hashed_password,
                                                   **dict(user))
    new_user = await user_repo.create_user(auth_user)
    return new_user


@router.get("/users/me/")
async def read_users_me(current_user: str = Depends(verify_current_user)):
    LOG.info("Getting current user")
    return current_user
