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

    def __init__(
        self
    ) -> None:
        pass