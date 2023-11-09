from fastapi import APIRouter

from . import router_auth_api, router_recipes_api

router = APIRouter(
    prefix='/api',
    tags=['api'],
)

router.include_router(router_auth_api.router)
router.include_router(router_recipes_api.router)
