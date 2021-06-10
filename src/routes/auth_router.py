from fastapi import APIRouter, Depends, Request, Response
from src.models.token_models import Token
from src.models.user_models import User, UserTemplate
from src.services.auth_service import AuthService
from src.util.cbv import cbv
from src.util.logging import get_logger

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

    @router.post("/logout")
    async def logout(self, request: Request, response: Response) -> None:
        return await self.auth_service.logout(request, response)


    @router.post("/refresh", response_model=Token)
    async def refresh_access_token(
        self,
        request: Request
    ) -> Token:
        return await self.auth_service.refresh_access_token(request)

    @router.post("/")
    async def create_new_user(self, user: UserTemplate) -> User:
        return await self.auth_service.register_user(user)
