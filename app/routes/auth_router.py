import secrets
from datetime import datetime, timedelta
from typing import Optional

from app.config import settings
from app.database.repos.user_repo import UserRepo
from app.models.token import Token
from app.models.user import AuthUserTemplate, User, UserTemplate
from app.util.logging import get_logger
from fastapi import (APIRouter, Depends, HTTPException, Request,
                     Response, responses, status)
from fastapi.security import HTTPBearer
from app.database.database import get_repo
from app.models.token import Token
from app.services.auth import AuthService
from app.util.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

logger = get_logger(__name__)
router = APIRouter(
        prefix="/auth",
        tags=["auth"],
        responses={404: {"description": "Not found"}},
    )

@cbv(router)
class AuthRouter:
    auth_service: AuthService = Depends(AuthService)
        
    @router.post("/login", response_model=Token)
    async def login(
        self,
        response: Response,
        username: str, 
        password: str
    ) -> Token:
        return await self.auth_service.login(response, username, password)


    @router.post("/refresh", response_model=Token)
    async def refresh_access_token(
        self,
        request: Request,
    ) -> Token:
        return await self.auth_service.refresh_access_token(request)

        '''
        @self.router.post("/")
        async def create_new_user(user: UserTemplate,
                                    user_repo: UserRepo = Depends(get_repo(UserRepo))) -> User:
            hashed_password = await jwt_auth.get_password_hash(user.password)
            auth_user: AuthUserTemplate = AuthUserTemplate(hashed_password=hashed_password,
                                                        **dict(user))
            new_user = await user_repo.create_user(auth_user)
            return new_user


        @self.router.get("/users/me/")
        async def read_users_me(current_user: str = Depends(verify_current_user)):
            logger.info("Getting current user")
            return current_user
        '''