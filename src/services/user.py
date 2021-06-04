import logging
from typing import Mapping, Optional
from fastapi.param_functions import Depends

from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer

from src.services.auth import AuthService
from src.config import settings
from jose import JWTError, ExpiredSignatureError, jwt
from src.util.logging import get_logger

logger = get_logger(__name__)


class UserService():

    def __init__(
        self
    ) -> None:
        pass