from sqlalchemy import (
    Column, ARRAY, Integer, Float, String, DateTime, Boolean, ForeignKey,
)
from sqlalchemy.dialects.postgresql import JSONB

from database import Base

import datetime


class BaseInfoMixin:
    id = Column(Integer, primary_key=True)
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)


class User(BaseInfoMixin, Base):
    __tablename__ = 'user'

    name = Column(String, nullable=False)
    login = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_conflict = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    def __repr__(self):
        return f'User {self.name} {self.id}'


class Recipe(Base):
    __tablename__ = "recipe"

    image = Column(String)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    recipe = Column(String, nullable=False)
    creator_id = Column(Integer, nullable=False)
    id = Column(Integer, primary_key=True)
    categories = Column(ARRAY(Integer))
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    popularity = Column(Integer, default=0)
    saver_ids = Column(ARRAY(Integer), default=[])


    def __repr__(self):
        return f'Recipe {self.name} {self.id}'
        

class Category(Base):
    __tablename__ = "category"

    name = Column(String, nullable=False, unique=True)
    id = Column(Integer, primary_key=True)


    def __repr__(self):
        return f'Category {self.name} {self.id}'
        