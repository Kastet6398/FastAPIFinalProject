from typing import List

from pydantic import BaseModel, EmailStr, Field

import settings


class AuthDetails(BaseModel):
    name: str = Field(min_length=3, max_length=50, examples=["Barak Obama"])
    login: str = Field(examples=["my_login"])
    email: EmailStr = Field(examples=["login@ukr.net"])
    password: str = Field(min_length=settings.Settings.MIN_PASSWORD_LENGTH, examples=["732$!714RF1#721n"])
    notes: str = Field(default="", max_length=settings.Settings.MAX_NOTES_LENGTH)


class AuthRegistered(BaseModel):
    success: bool = Field(examples=[True])
    id: int = Field(examples=[656])
    login: str = Field(examples=["my_login"])


class AuthLogin(BaseModel):
    login: str = Field(examples=["my_login"])
    password: str = Field(min_length=settings.Settings.MIN_PASSWORD_LENGTH, examples=["732$!714RF1#721n"])


class Recipe(BaseModel):
    id: int = Field()
    name: str = Field(examples=['Yakiniku'])
    description: str = Field(examples=['A very tasty food!'])
    recipe: str = Field(examples=['1) ...\n2) ...\n3) ...'])
    image: str = Field(default="", examples=['https://'])
    categories: List[int] = Field(default=[])
    popularity: int = Field(default=0)
