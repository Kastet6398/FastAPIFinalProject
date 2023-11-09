import re
from typing import List

from fastapi import (APIRouter, Depends, Form, HTTPException, Query, Request,
                     status)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr

import dao
import settings
from app.auth import dependencies
from app.auth.auth_lib import AuthHandler, AuthLibrary

router = APIRouter(
    tags=['menu', 'landing'],
    include_in_schema=False
)

templates = Jinja2Templates(directory='app\\templates')


@router.get('/menu')
@router.post('/menu')
async def get_menu(request: Request,
                   sort: str = Query(""),
                   dish_name: str = Query(""),
                   saved: bool = Query(False),
                   categories: List[int] = Query([]),
                   page: int = Query(0),
                   user=Depends(dependencies.get_current_user_optional)
                   ):
    if saved:
        if user:
            all_fetched_recipes = await dao.fetch_saved_recipes(user.id)
        else:
            status_code = status.HTTP_403_FORBIDDEN
            context = {
                'request': request,
                'title': 'User error',
                'content': 'You must be logged in to view saved recipes.',
                'code': status_code,
                'user': user,
            }

            return templates.TemplateResponse(
                '400.html',
                context=context,
                status_code=status_code
            )
    else:
        all_fetched_recipes = await dao.fetch_recipes()
    recipes = []
    skip = page * settings.Settings.NUM_RECIPES_ON_PAGE
    filtered_recipes = []
    fetched_categories = await dao.fetch_categories()
    context = {
        'request': request,
        'user': user,
        'categories': fetched_categories,
        'page': page,
        'sort': sort,
        'title': ('Saved' if saved else 'All') + ' recipes',
        'dish_name': dish_name,
        'saved': saved,
        'selected_categories': categories
    }

    if categories:
        filtered_recipes = list(filter(
            lambda x: x[0].categories and set(x[0].categories).issubset(set(categories)),
            all_fetched_recipes))
        context['title'] = ('Saved recipes' if saved else 'Recipes')\
            + f' with categor{"ies" if len(categories) > 1 else "y"} {", ".join([fetched_categories[id - 1][0].name for id in categories])}'
    else:
        filtered_recipes = all_fetched_recipes

    if re.sub(r"\s+", '', dish_name):
        context["dish_name"] = dish_name
        for dish in filtered_recipes:
            if dish_name.lower() in dish[0].name.lower():
                recipes.append(dish)
        context['title'] = f'{dish_name} search results' + (' in saved recipes' if saved else '')
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

    context['menu'] = recipes
    context['previous_page'] = page - 1

    if skip < len(recipes) // settings.Settings.NUM_RECIPES_ON_PAGE:
        context['next_page'] = page + 1

    return templates.TemplateResponse(
        'menu.html',
        context=context,
    )


@router.post('/create-recipe-final')
async def create_recipe_final(
    request: Request,
    image: str = Form(""),
    name: str = Form(),
    description: str = Form(),
    recipe: str = Form(),
    categories: List[int] = Form([]),
    user=Depends(dependencies.get_current_user_optional)
):
    if user:

        if await dao.get_recipe_by_name(name):
            status_code = status.HTTP_406_NOT_ACCEPTABLE
            context = {
                'request': request,
                'title': 'Recipe error',
                'content': f'Recipe {name} already exists.',
                'code': status_code,
                'user': user,
            }

            return templates.TemplateResponse(
                '400.html',
                context=context,
                status_code=status_code
            )
        recipe_id = (await dao.create_recipe(
            name=name,
            description=description,
            image=image,
            recipe=recipe,
            categories=categories,
            creator_id=user.id)).id

        return RedirectResponse(f"/recipe/{recipe_id}")

    status_code = status.HTTP_403_FORBIDDEN
    context = {
        'request': request,
        'title': 'User error',
        'content': 'You must be logged in to access this page (/create-recipe-final).',
        'code': status_code,
        'user': user,
    }

    return templates.TemplateResponse(
        '400.html',
        context=context,
        status_code=status_code
    )


@router.post('/update-recipe-final')
async def update_recipe_final(
    request: Request,
    recipe_id: int = Form(),
    image: str = Form(""),
    name: str = Form(),
    description: str = Form(),
    recipe: str = Form(),
    categories: List[int] = Form([]),
    user=Depends(dependencies.get_current_user_optional)
):
    if user:

        if not (recipe_object := await dao.get_recipe_by_id(recipe_id)):
            status_code = status.HTTP_404_NOT_FOUND
            context = {
                'request': request,
                'title': 'Recipe error',
                'content': f'Recipe #{recipe_id} does not exist.',
                'code': status_code,
                'user': user,
            }

            return templates.TemplateResponse(
                '400.html',
                context=context,
                status_code=status_code
            )

        if not (user.is_superuser or recipe_object.creator_id == user.id):
            status_code = status.HTTP_403_FORBIDDEN
            context = {
                'request': request,
                'title': 'Recipe error',
                'content': "You don't have permission to edit this recipe.",
                'code': status_code,
                'user': user,
            }

            return templates.TemplateResponse(
                '400.html',
                context=context,
                status_code=status_code
            )

        if (recipe_exists := (await dao.get_recipe_by_name(name))) and recipe_exists.id != recipe_id:
            status_code = status.HTTP_406_NOT_ACCEPTABLE
            context = {
                'request': request,
                'title': 'Recipe error',
                'content': f'Recipe {name} already exists.',
                'code': status_code,
                'user': user,
            }

            return templates.TemplateResponse(
                '400.html',
                context=context,
                status_code=status_code
            )
        await dao.update_recipe(
            name=name,
            description=description,
            image=image,
            recipe=recipe,
            categories=categories,
            recipe_id=recipe_id
            )

        return RedirectResponse(f"/recipe/{recipe_id}")

    status_code = status.HTTP_403_FORBIDDEN
    context = {
        'request': request,
        'title': 'User error',
        'content': 'You must be logged in to access this page (/update-recipe-final).',
        'code': status_code,
        'user': user,
    }

    return templates.TemplateResponse(
        '400.html',
        context=context,
        status_code=status_code
    )


@router.get('/create-recipe')
async def create_recipe(request: Request, user=Depends(dependencies.get_current_user_optional)):
    if user:
        context = {
            'request': request,
            'title': 'Create new recipe',
            'user': user,
            'categories': await dao.fetch_categories(),
        }

        return templates.TemplateResponse(
            'create_recipe.html',
            context=context,
        )
    status_code = status.HTTP_403_FORBIDDEN
    context = {
        'request': request,
        'title': 'User error',
        'content': 'You must be logged in to access this page (/create-recipe).',
        'code': status_code,
        'user': user,
    }

    return templates.TemplateResponse(
        '400.html',
        context=context,
        status_code=status_code
    )


@router.get('/update-recipe/{recipe_id}')
async def update_recipe(request: Request, recipe_id: int, user=Depends(dependencies.get_current_user_optional)):
    if user:
        if not (recipe_object := await dao.get_recipe_by_id(recipe_id)):
            status_code = status.HTTP_404_NOT_FOUND
            context = {
                'request': request,
                'title': 'Recipe error',
                'content': f'Recipe #{recipe_id} does not exist.',
                'code': status_code,
                'user': user,
            }

            return templates.TemplateResponse(
                '400.html',
                context=context,
                status_code=status_code
            )

        if not (user.is_superuser or recipe_object.creator_id == user.id):
            status_code = status.HTTP_403_FORBIDDEN
            context = {
                'request': request,
                'title': 'Recipe error',
                'content': "You don't have permission to edit this recipe.",
                'code': status_code,
                'user': user,
            }

            return templates.TemplateResponse(
                '400.html',
                context=context,
                status_code=status_code
            )

        context = {
            'request': request,
            'recipe': recipe_object,
            'title': f'Update recipe #{recipe_id}',
            'user': user,
            'categories': await dao.fetch_categories(),
        }

        return templates.TemplateResponse(
            'update_recipe.html',
            context=context,
        )
    status_code = status.HTTP_403_FORBIDDEN
    context = {
        'request': request,
        'title': 'User error',
        'content': 'You must be logged in to access this page (/update-recipe).',
        'code': status_code,
        'user': user,
    }

    return templates.TemplateResponse(
        '400.html',
        context=context,
        status_code=status_code
    )


@router.get('/recipe/{id}')
@router.post('/recipe/{id}')
async def recipe(request: Request, id: int, user=Depends(dependencies.get_current_user_optional)):
    recipe = await dao.get_recipe_by_id(id)
    if not recipe:
        status_code = status.HTTP_404_NOT_FOUND

        context = {
            'request': request,
            'title': 'Recipe error',
            'content': f'Recipe with ID {id} does not exist.',
            'code': status_code,
            'user': user,
        }

        return templates.TemplateResponse(
            '400.html',
            context=context,
            status_code=status_code
        )

    await dao.increase_recipe_popularity(id)
    context = {
        'request': request,
        'user': user,
        'title': f'Recipe {recipe.name}',
        'recipe': recipe,
        'categories': await dao.fetch_categories(),
    }
    return templates.TemplateResponse(
        'recipe.html',
        context=context,
    )


@router.get('/about-us')
async def about_us(request: Request, user=Depends(dependencies.get_current_user_optional)):
    context = {
        'request': request,
        'title': 'About us',
        'user': user,
    }

    return templates.TemplateResponse(
        'about_us.html',
        context=context,
    )


@router.get('/message')
async def message(request: Request, user=Depends(dependencies.get_current_user_optional)):
    if user:
        context = {
            'request': request,
            'title': 'Write a message',
            'user': user,
        }

        return templates.TemplateResponse(
            'message_to_all.html',
            context=context,
        )
    status_code = status.HTTP_403_FORBIDDEN
    context = {
        'request': request,
        'title': 'User error',
        'content': 'You must be logged in to access this page (/message/).',
        'code': status_code,
        'user': user,
    }

    return templates.TemplateResponse(
        '400.html',
        context=context,
        status_code=status_code
    )


@router.get('/register')
async def register(request: Request, user=Depends(dependencies.get_current_user_optional)):
    if user:
        return RedirectResponse("/menu/")
    context = {
        'request': request,
        'title': 'Register',
        'min_password_length': settings.Settings.MIN_PASSWORD_LENGTH,
        'max_notes_length': settings.Settings.MAX_NOTES_LENGTH,
        'user': user,
    }

    return templates.TemplateResponse(
        'register.html',
        context=context,
    )


@router.get('/login')
async def login(request: Request, user=Depends(dependencies.get_current_user_optional)):
    if user:
        return RedirectResponse("/menu/")
    context = {
        'request': request,
        'title': 'Login',
        'min_password_length': settings.Settings.MIN_PASSWORD_LENGTH,
        'user': user,
    }

    return templates.TemplateResponse(
        'login.html',
        context=context,
    )


@router.get('/delete-my-account')
async def delete_my_account(request: Request, user=Depends(dependencies.get_current_user_optional)):
    if user:
        context = {
            'request': request,
            'title': 'Delete my account',
            'user': user,
        }
        return templates.TemplateResponse(
            'delete_my_account.html',
            context=context
        )
    status_code = status.HTTP_403_FORBIDDEN
    context = {
        'request': request,
        'title': 'User error',
        'content': 'You must be logged in to access this page (/delete-my-account).',
        'code': status_code,
        'user': user,
    }

    return templates.TemplateResponse(
        '400.html',
        context=context,
        status_code=status_code
    )


@router.get('/delete-my-account-final')
async def delete_my_account_final(request: Request, user=Depends(dependencies.get_current_user_optional)):
    if user:
        await dao.delete_user(user.id)
        return RedirectResponse("/menu/")
    status_code = status.HTTP_403_FORBIDDEN
    context = {
        'request': request,
        'title': 'User error',
        'content': 'You must be logged in to access this page (/delete-my-account-final).',
        'code': status_code,
        'user': user,
    }

    return templates.TemplateResponse(
        '400.html',
        context=context,
        status_code=status_code
    )


@router.get('/delete-recipe/{recipe_id}')
async def delete_recipe(request: Request, recipe_id: int, user=Depends(dependencies.get_current_user_optional)):
    if user:
        if not (recipe_object := await dao.get_recipe_by_id(recipe_id)):
            status_code = status.HTTP_404_NOT_FOUND
            context = {
                'request': request,
                'title': 'Recipe error',
                'content': f'Recipe #{recipe_id} does not exist.',
                'code': status_code,
                'user': user,
            }

            return templates.TemplateResponse(
                '400.html',
                context=context,
                status_code=status_code
            )

        if not (user.is_superuser or recipe_object.creator_id == user.id):
            status_code = status.HTTP_403_FORBIDDEN
            context = {
                'request': request,
                'title': 'Recipe error',
                'content': "You don't have permission to delete this recipe.",
                'code': status_code,
                'user': user,
            }

            return templates.TemplateResponse(
                '400.html',
                context=context,
                status_code=status_code
            )
        context = {
            'request': request,
            'title': f'Delete recipe {recipe_object.name}',
            'user': user,
            'recipe_id': recipe_id
        }
        return templates.TemplateResponse(
            'delete_recipe.html',
            context=context
        )

    status_code = status.HTTP_403_FORBIDDEN
    context = {
        'request': request,
        'title': 'User error',
        'content': 'You must be logged in to delete recipes.',
        'code': status_code,
        'user': user,
    }

    return templates.TemplateResponse(
        '400.html',
        context=context,
        status_code=status_code
    )


@router.get('/delete-recipe-final/{recipe_id}')
async def delete_recipe_final(
    request: Request,
    recipe_id: int,
    user=Depends(dependencies.get_current_user_optional)
):
    if user:
        if not (recipe_object := await dao.get_recipe_by_id(recipe_id)):
            status_code = status.HTTP_404_NOT_FOUND
            context = {
                'request': request,
                'title': 'Recipe error',
                'content': f'Recipe #{recipe_id} does not exist.',
                'code': status_code,
                'user': user,
            }

            return templates.TemplateResponse(
                '400.html',
                context=context,
                status_code=status_code
            )

        if not (user.is_superuser or recipe_object.creator_id == user.id):
            status_code = status.HTTP_403_FORBIDDEN
            context = {
                'request': request,
                'title': 'Recipe error',
                'content': "You don't have permission to delete this recipe.",
                'code': status_code,
                'user': user,
            }

            return templates.TemplateResponse(
                '400.html',
                context=context,
                status_code=status_code
            )
        await dao.delete_recipe(recipe_id)
        return RedirectResponse("/menu/")

    status_code = status.HTTP_403_FORBIDDEN
    context = {
        'request': request,
        'title': 'User error',
        'content': 'You must be logged in to delete recipes.',
        'code': status_code,
        'user': user,
    }

    return templates.TemplateResponse(
        '400.html',
        context=context,
        status_code=status_code
    )


@router.get('/save-recipe/{recipe_id}')
async def save_recipe(request: Request, recipe_id: int, user=Depends(dependencies.get_current_user_optional)):
    if user:
        if not await dao.get_recipe_by_id(recipe_id):
            status_code = status.HTTP_404_NOT_FOUND
            context = {
                'request': request,
                'title': 'Recipe error',
                'content': f'Recipe #{recipe_id} does not exist.',
                'code': status_code,
                'user': user,
            }

            return templates.TemplateResponse(
                '400.html',
                context=context,
                status_code=status_code
            )
        await dao.save_recipe(recipe_id, user.id)
        return RedirectResponse("/menu?saved=True")

    status_code = status.HTTP_403_FORBIDDEN
    context = {
        'request': request,
        'title': 'User error',
        'content': 'You must be logged in to save recipes.',
        'code': status_code,
        'user': user,
    }

    return templates.TemplateResponse(
        '400.html',
        context=context,
        status_code=status_code
    )


@router.get('/unsave-recipe/{recipe_id}')
async def unsave_recipe(request: Request, recipe_id: int, user=Depends(dependencies.get_current_user_optional)):
    if user:
        if not await dao.get_recipe_by_id(recipe_id):
            status_code = status.HTTP_404_NOT_FOUND
            context = {
                'request': request,
                'title': 'Recipe error',
                'content': f'Recipe #{recipe_id} does not exist.',
                'code': status_code,
                'user': user,
            }

            return templates.TemplateResponse(
                '400.html',
                context=context,
                status_code=status_code
            )
        await dao.unsave_recipe(recipe_id, user.id)
        return RedirectResponse("/menu?saved=True")

    status_code = status.HTTP_403_FORBIDDEN
    context = {
        'request': request,
        'title': 'User error',
        'content': 'You must be logged in to unsave recipes.',
        'code': status_code,
        'user': user,
    }

    return templates.TemplateResponse(
        '400.html',
        context=context,
        status_code=status_code
    )


@router.post('/register-final')
async def register_final(request: Request,
                         name: str = Form(),
                         login: str = Form(),
                         email: EmailStr = Form(),
                         notes: str = Form(default=''),
                         password: str = Form(),
                         user=Depends(dependencies.get_current_user_optional)
                         ):
    if re.search(r"\s", login):
        status_code = status.HTTP_406_NOT_ACCEPTABLE
        context = {
            'request': request,
            'title': 'User error',
            'content': 'Login cannot contain spaces.',
            'code': status_code,
            'user': user,
        }

        return templates.TemplateResponse(
            '400.html',
            context=context,
            status_code=status_code
        )

    if user:
        return RedirectResponse("/menu/")

    is_login_already_used = await dao.get_user_by_login(login)
    if is_login_already_used:
        status_code = status.HTTP_406_NOT_ACCEPTABLE
        context = {
            'request': request,
            'title': 'User error',
            'content': f'User {login} already exists.',
            'code': status_code,
            'user': user,
        }

        return templates.TemplateResponse(
            '400.html',
            context=context,
            status_code=status_code
        )

    is_email_already_used = await dao.get_user_by_email(email)
    if is_email_already_used:
        status_code = status.HTTP_406_NOT_ACCEPTABLE
        context = {
            'request': request,
            'title': 'User error',
            'content': f'User with email {email} already exists.',
            'code': status_code,
            'user': user,
        }

        return templates.TemplateResponse(
            '400.html',
            context=context,
            status_code=status_code
        )

    hashed_password = await AuthHandler.get_password_hash(password)

    user_data = await dao.create_user(
        name=name,
        login=login,
        email=email,
        password=hashed_password,
        notes=notes,
    )

    token = await AuthHandler.encode_token(user_data[0])

    redirect_response = RedirectResponse("/menu")

    redirect_response.set_cookie(key='token', value=token, httponly=True, max_age=1000)

    return redirect_response


@router.post('/login-final')
async def login_final(
    request: Request,
    login: str = Form(),
    password: str = Form(),
    user=Depends(dependencies.get_current_user_optional)
):
    response = RedirectResponse("/menu/")
    if not user:
        try:
            logged_in_user = await AuthLibrary.authenticate_user(login=login, password=password)
        except HTTPException as e:
            status_code = e.status_code
            context = {
                'request': request,
                'title': 'User error',
                'content': e.detail,
                'code': status_code,
                'user': user,
            }

            return templates.TemplateResponse(
                '400.html',
                context=context,
                status_code=status_code
            )

        token = await AuthHandler.encode_token(logged_in_user.id)
        response.set_cookie(key='token', value=token, httponly=True, max_age=1000)

    return response


@router.get('/logout')
async def logout(request: Request):
    response = RedirectResponse('/menu/')
    response.delete_cookie('token')
    return response
