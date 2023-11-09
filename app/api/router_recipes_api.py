from fastapi import Query, APIRouter, status, HTTPException, Request, Response, Depends

from app.auth.auth_lib import AuthHandler, AuthLibrary
import dao
from app.auth import dependencies
from typing import List
from .schemas import Recipe
import settings
import re


router = APIRouter(
    prefix='/recipes',
    tags=['recipes'],
)

@router.get('/delete-recipe/{recipe_id}')
async def delete_recipe(request: Request,
                         recipe_id: int,
                     user=Depends(dependencies.get_current_user_required)):

    if not (recipe_object := await dao.get_recipe_by_id(recipe_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Recipe #{recipe_id} does not exist.')

    if not (user.is_superuser or recipe_object.creator_id == user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to delete this recipe.")

    await dao.delete_recipe(recipe_id)
    return {"success": True}
    
    
@router.post('/update-recipe')
async def update_recipe(
    request: Request,
    recipe_id: int,
    name: str,
    description: str,
    recipe: str,
    categories: List[int] = Query([]),
    image: str = "",
    user=Depends(dependencies.get_current_user_required)
):

    if not (recipe_object := await dao.get_recipe_by_id(recipe_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Recipe #{recipe_id} does not exist.')

    if not (user.is_superuser or recipe_object.creator_id == user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to delete this recipe.")


    if (recipe_exists := (await dao.get_recipe_by_name(name))) and recipe_exists.id != recipe_id:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f'Recipe {name} already exists.')

    await dao.update_recipe(name=name, description=description, image=image, recipe=recipe, categories=categories, recipe_id=recipe_id)
    
    return Recipe(name=name, description=description, recipe=recipe, image=image, categories=categories)

    
@router.post('/create-recipe')
async def create_recipe(
    request: Request,
    name: str,
    description: str,
    recipe: str,
    categories: List[int] = Query([]),
    image: str = "",
    user=Depends(dependencies.get_current_user_required)
):
    if await dao.get_recipe_by_name(name):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f'Recipe {name} already exists.')

    await dao.create_recipe(name=name, description=description, image=image, recipe=recipe, categories=categories, creator_id=user.id)
    
    return Recipe(name=name, description=description, recipe=recipe, image=image, categories=categories)


@router.get('/recipe/{recipe_id}')
async def recipe(request: Request, recipe_id: int, user=Depends(dependencies.get_current_user_optional)):
    recipe = await dao.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Recipe #{recipe_id} does not exist.')

    await dao.increase_recipe_popularity(recipe_id)
    
    return Recipe(name=recipe.name, description=recipe.description, recipe=recipe.recipe, image=recipe.image, categories=recipe.categories)


@router.get('/recipe/{recipe_id}')
async def recipe(request: Request, recipe_id: int, user=Depends(dependencies.get_current_user_optional)):
    recipe = await dao.get_recipe_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Recipe #{recipe_id} does not exist.')

    await dao.increase_recipe_popularity(recipe_id)
    
    return Recipe(name=recipe.name, description=recipe.description, recipe=recipe.recipe, image=recipe.image, categories=recipe.categories)
    
    

@router.get('/menu')
@router.post('/menu')
async def get_menu(request: Request, sort: str = Query(""), dish_name: str = Query(""), 
    categories: List[int] = Query([]), page: int = 0, user=Depends(dependencies.get_current_user_optional)):
    recipes = []
    skip = page * settings.Settings.NUM_RECIPES_ON_PAGE
    all_fetched_recipes = await dao.fetch_recipes()
    
    if categories:
        filtered_recipes = list(filter(lambda x: set(x[0].categories).issubset(set(categories)), all_fetched_recipes))
    else:
        filtered_recipes = all_fetched_recipes

    if re.sub(r"\s+", '', dish_name):
        for dish in filtered_recipes:
            if dish_name.lower() in dish[0].name.lower():
                recipes.append(dish)
    else:
        recipes = filtered_recipes

    
    if sort == "popularity-asc":
        recipes = sorted(recipes, key=lambda x: x[0].popularity)
    elif sort == "popularity-desc":
        recipes = sorted(recipes, key=lambda x: x[0].popularity, reverse=True)
    elif sort == "a-z":
        recipes = sorted(recipes, key=lambda x: x[0].name.lower())
    elif sort == "z-a":
        recipes = sorted(recipes, key=lambda x: x[0].name.lower(), reverse=True)

    recipes = recipes[skip:skip + settings.Settings.NUM_RECIPES_ON_PAGE]

    
        
    
    return [Recipe(id=recipe[0].id, name=recipe[0].name, description=recipe[0].description, recipe=recipe[0].recipe, image=recipe[0].image, categories=recipe[0].categories, popularity=recipe[0].popularity) for recipe in recipes]
    
@router.get('/saved-recipes/')
@router.post('/saved-recipes/')
async def saved_recipes(request: Request, sort: str = Query(""), dish_name: str = Query(""),
    categories: List[int] = Query([]), page: int = 0, user=Depends(dependencies.get_current_user_required)):
    
    skip = page * 10
    all_fetched_recipes = await dao.fetch_saved_recipes(user.id)
   
    recipes = []
    if categories:
        filtered_recipes = list(filter(lambda x: x[0].categories and set(x[0].categories).issubset(set(categories)), all_fetched_recipes))
    else:
        filtered_recipes = all_fetched_recipes

    if re.sub(r"\s+", '', dish_name):
        for dish in filtered_recipes:
            if dish_name.lower() in dish[0].name.lower():
                recipes.append(dish)
    else:
        recipes = filtered_recipes

    
    
    if sort == "popularity-asc":
        recipes = sorted(recipes, key=lambda x: x[0].popularity)
    elif sort == "popularity-desc":
        recipes = sorted(recipes, key=lambda x: x[0].popularity, reverse=True)
    elif sort == "a-z":
        recipes = sorted(recipes, key=lambda x: x[0].name.lower())
    elif sort == "z-a":
        recipes = sorted(recipes, key=lambda x: x[0].name.lower(), reverse=True)

    recipes = recipes[skip:skip + settings.Settings.NUM_RECIPES_ON_PAGE]

    
    return [Recipe(id=recipe[0].id, name=recipe[0].name, description=recipe[0].description, recipe=recipe[0].recipe, image=recipe[0].image, categories=recipe[0].categories, popularity=recipe[0].popularity) for recipe in recipes]
    



@router.get('/save-recipe/{recipe_id}')
async def save_recipe(request: Request, recipe_id: int, user=Depends(dependencies.get_current_user_required)):
    if not await dao.get_recipe_by_id(recipe_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Recipe #{recipe_id} does not exist.')

    await dao.save_recipe(recipe_id, user.id)
    
    return {"saved": True}
    
@router.get('/unsave-recipe/{recipe_id}')
async def unsave_recipe(request: Request, recipe_id: int, user=Depends(dependencies.get_current_user_required)):
    if not await dao.get_recipe_by_id(recipe_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Recipe #{recipe_id} does not exist.')

    await dao.unsave_recipe(recipe_id, user.id)
    
    return {"unsaved": True}