from passlib.context import CryptContext
from fastapi.exceptions import HTTPException
from fastapi import status
from datetime import datetime, timedelta
from jose import JWTError, ExpiredSignatureError, jwt
from app.config import settings
from typing import Mapping

class JWTAuth():
    def __init__(self,
        secret_key: str,
        algorithm: str,
        pwd_context: CryptContext,
    ) -> None:
        self.pwd_context = pwd_context
        self.secret_key = secret_key
        self.algorithm = algorithm

        self.invalid_token_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        self.token_expired_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )


    async def create_token(self, data: dict, expires_minutes: int) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.hashing_algorithm)
        return encoded_jwt

    def verify_token(self, token) -> Mapping:
        try:
            payload = jwt.decode(token, 
                                 settings.secret_key, 
                                 algorithms=[self.algorithm],
                                 options={
                                     "require_sub": True
                                 })
            return payload
        except ExpiredSignatureError:
            raise self.token_expired_exception
        except JWTError:
            raise self.invalid_token_exception
    
    def decode_token_without_exp_verification(self, token) -> Mapping:
        try:
            payload = jwt.decode(token, 
                                 settings.secret_key, 
                                 algorithms=[self.algorithm],
                                 options={
                                     "require_sub": True,
                                     "verify_exp": False
                                 })
            return payload
        except JWTError:
            raise self.invalid_token_exception

    
    async def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)
        
    async def get_password_hash(self, password):
        return self.pwd_context.hash(password)