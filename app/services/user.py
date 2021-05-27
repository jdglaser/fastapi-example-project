import logging
from typing import Mapping, Optional
from fastapi.param_functions import Depends

from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer

from app.services.auth import AuthService
from app.config import settings
from jose import JWTError, ExpiredSignatureError, jwt
from app.util.logging import get_logger

logger = get_logger(__name__)


class UserService():
    auth_scheme = HTTPBearer()

    def __init__(
        self,
        token: Optional[HTTPAuthorizationCredentials] = Depends(auth_scheme)
    ) -> None:
        self.token = token

    def __call__(self) -> str:
        logger.info("Called __Call__")
        return self.get_current_user()
    
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
            raise AuthService.token_expired_exception
        except JWTError:
            raise AuthService.invalid_token_exception

    def get_current_user(self) -> str:
        logger.info("Get current user called")
        if not self.token:
            raise AuthService.invalid_token_exception
        payload = self.verify_token(self.token.credentials)
        username: Optional[str] = payload.get("sub")
        if not username:
            raise AuthService.invalid_token_exception
        return username