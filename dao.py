from sqlalchemy import delete, insert, select, text, update

from database import async_session_maker
from models import Category, Recipe, User


async def create_user(
        name: str,
        login: str,
        email: str,
        password: str,
        notes: str = '',
        is_conflict: bool = False
        ):
    async with async_session_maker() as session:
        query = insert(User).values(
            name=name,
            login=login,
            email=email,
            password=password,
            notes=notes,
            is_conflict=is_conflict
            ).returning(User.id, User.login)
        data = await session.execute(query)
        await session.commit()
        return data.fetchone()


async def create_superuser_from_user(user_id: int):
    async with async_session_maker() as session:
        query = update(User).where(User.id == user_id).values(is_superuser=True)
        await session.execute(query)
        await session.commit()


async def create_category(name: str):
    async with async_session_maker() as session:
        query = insert(Category).values(name=name).returning(Category.id, Category.name)
        data = await session.execute(query)
        await session.commit()
        return data.fetchone()


async def create_recipe(
        name: str,
        description: str,
        recipe: str,
        image: str,
        creator_id: int,
        categories: list = []
        ):
    async with async_session_maker() as session:
        query = insert(Recipe).values(
            name=name,
            description=description,
            recipe=recipe,
            image=image,
            categories=categories,
            creator_id=creator_id
            ).returning(Recipe.id, Recipe.name)
        data = await session.execute(query)
        await session.commit()
        return data.fetchone()


async def update_recipe(
        recipe_id: int,
        name: str,
        description: str,
        recipe: str,
        image: str = "",
        categories: list = []
        ):
    async with async_session_maker() as session:
        query = update(Recipe).where(Recipe.id == recipe_id).values(
            name=name,
            description=description,
            recipe=recipe,
            image=image,
            categories=categories
            )
        await session.execute(query)
        await session.commit()


async def get_user_by_id(user_id: int):
    async with async_session_maker() as session:
        query = select(User).filter_by(id=user_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def get_user_by_login(user_login: str):
    async with async_session_maker() as session:
        query = select(User).filter_by(login=user_login)
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def get_recipe_by_id(recipe_id: str):
    async with async_session_maker() as session:
        query = select(Recipe).filter_by(id=recipe_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def get_recipe_by_name(recipe_name: str):
    async with async_session_maker() as session:
        query = select(Recipe).filter_by(name=recipe_name)
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def get_category_by_id(category_id: str):
    async with async_session_maker() as session:
        query = select(Category).filter_by(id=category_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def save_recipe(recipe_id: int, saver_id: int):
    async with async_session_maker() as session:
        query = update(Recipe).where(Recipe.id == recipe_id).values(
            saver_ids=text('array_append(saver_ids, :saver_id)')
            )
        await session.execute(query, {"saver_id": saver_id})
        await session.commit()


async def unsave_recipe(recipe_id: int, saver_id: int):
    async with async_session_maker() as session:
        query = update(Recipe).where(Recipe.id == recipe_id).values(
            saver_ids=text('array_remove(saver_ids, :saver_id)')
            )
        await session.execute(query, {"saver_id": saver_id})
        await session.commit()


async def update_user(user_id: int):
    async with async_session_maker() as session:
        query = update(User).where(User.id == user_id).values(name="222")
        await session.execute(query)
        await session.commit()


async def increase_recipe_popularity(recipe_id: int):
    async with async_session_maker() as session:
        popularity = (await get_recipe_by_id(recipe_id)).popularity
        query = update(Recipe).where(Recipe.id == recipe_id).values(
            popularity=(popularity if popularity else 0) + 1
            )
        await session.execute(query)
        await session.commit()


async def fetch_users(skip: int = 0, limit: int = 10):
    async with async_session_maker() as session:
        query = select(User).offset(skip).limit(limit)
        result = await session.execute(query)
        return list(result)


async def get_user_by_email(email: str):
    async with async_session_maker() as session:
        query = select(User).filter_by(email=email)
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def fetch_recipes():
    async with async_session_maker() as session:
        query = select(Recipe)
        result = await session.execute(query)
        return list(result)


async def fetch_saved_recipes(saver_id: int):
    async with async_session_maker() as session:
        query = select(Recipe).filter(Recipe.saver_ids.any(saver_id))
        result = await session.execute(query)
        return list(result)


async def fetch_categories():
    async with async_session_maker() as session:
        query = select(Category)
        result = await session.execute(query)
        return sorted(result, key=lambda category: category[0].id)


async def delete_user(user_id: int):
    async with async_session_maker() as session:
        query = delete(User).where(User.id == user_id)
        await session.execute(query)
        await session.commit()


async def delete_recipe(recipe_id: int):
    async with async_session_maker() as session:
        query = delete(Recipe).where(Recipe.id == recipe_id)
        await session.execute(query)
        await session.commit()
