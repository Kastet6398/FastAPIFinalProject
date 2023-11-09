import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    DATABASE_NAME = os.getenv('DATABASE_NAME', '')
    DATABASE_USER = os.getenv('DATABASE_USER', '')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', '')
    DATABASE_HOST = os.getenv('DATABASE_HOST', '')
    DATABASE_PORT = os.getenv('DATABASE_PORT', '')
    MAX_NOTES_LENGTH = 400
    TOKEN_SECRET = os.getenv('TOKEN_SECRET') or ''
    TOKEN_ALGORITHM = os.getenv('TOKEN_ALGORITHM') or ''
    MIN_PASSWORD_LENGTH = 8
    NUM_RECIPES_ON_PAGE = 9
