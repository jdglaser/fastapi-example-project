from src.models.user import User
from fastapi.exceptions import HTTPException
from src.database.repos.user_repo import UserRepo
from fastapi.param_functions import Depends
from src.util.logging import get_logger
from fastapi import APIRouter, status
from src.util.cbv import cbv
from src.services.auth import AuthService


logger = get_logger(__name__)
router = APIRouter(
        prefix="/user",
        tags=["user"],
        responses={404: {"description": "Not found"}},
    )

@cbv(router)
class AuthRouter:
    username: str = Depends(AuthService.verify_current_user)
    auth_service: AuthService = Depends()
    user_repo: UserRepo = Depends()

    @router.get("/me")
    async def get_me(self) -> User:
      user = await self.user_repo.find_user(self.username)
      if not user:
        raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail=f"Cannot find user {self.username}"
        )
      return user