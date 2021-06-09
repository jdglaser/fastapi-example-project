import secrets
from datetime import datetime, timedelta
from typing import Mapping, Optional

from src.config import settings
from src.database.repos.user_repo import UserRepo
from src.models.token import Token
from src.models.user import AuthUserTemplate, User, UserTemplate
from src.util.logging import get_logger
from fastapi import (APIRouter, Depends, HTTPException, Request,
                     Response, responses, status)
from fastapi.security import HTTPBearer
from src.models.token import Token
from src.services.auth import AuthService
from src.util.cbv import cbv
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
        request: Request
    ) -> Token:
        logger.info("refreshing")
        return await self.auth_service.refresh_access_token(request)

    @router.post("/")
    async def create_new_user(self, user: UserTemplate) -> User:
        return await self.auth_service.register_user(user)