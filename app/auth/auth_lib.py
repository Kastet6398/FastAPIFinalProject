import jwt

from fastapi import HTTPException, Security, status, Request
from passlib.context import CryptContext
from datetime import datetime, timedelta

from pydantic import EmailStr

import settings
import dao


class AuthHandler:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = settings.Settings.TOKEN_SECRET
    algorithm = settings.Settings.TOKEN_ALGORITHM

    @classmethod
    async def get_password_hash(cls, password: str) -> str:
        return cls.pwd_context.hash(password)

    @classmethod
    async def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(plain_password, hashed_password)

    @classmethod
    async def encode_token(cls, user_id: int) -> str:
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=5),
            'iat': datetime.utcnow(),
            'user_id': user_id
        }
        return jwt.encode(
            payload,
            cls.secret,
            algorithm=cls.algorithm,
        )

    @classmethod
    async def decode_token(cls, token: str) -> dict:
        try:
            payload = jwt.decode(token, cls.secret, algorithms=[cls.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Signature has expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')

    @classmethod
    async def decode_token_web(cls, token: str | None) -> dict:
        try:
            payload = jwt.decode(token, cls.secret, algorithms=[cls.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return {}
        except jwt.InvalidTokenError:
            return {}

class AuthLibrary:

    @classmethod
    async def authenticate_user(cls, login: EmailStr, password: str):
        user = await dao.get_user_by_login(login)
        if not (user and await AuthHandler.verify_password(password, user.password)):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=f'Incorrect login "{login}" or password'
            )
        return user