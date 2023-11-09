from fastapi import Depends, HTTPException, Request, status

import dao
from app.auth import auth_lib


async def get_token(request: Request):
    token = request.cookies.get('token')
    if not token:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='Token not presented'
        )
    return token


async def get_token_web(request: Request):
    token = request.cookies.get('token')
    return token


async def get_current_user_required(token=Depends(get_token)):
    payload = await auth_lib.AuthHandler.decode_token(token)
    user_id = payload.get('user_id')
    if not user_id:
        # if not None
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='user_id not presented'
        )
    user = await dao.get_user_by_id(int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='user not found'
        )
    return user


async def get_current_user_optional(token=Depends(get_token_web)):
    payload = await auth_lib.AuthHandler.decode_token_web(token)

    user_id = payload.get('user_id')
    if not user_id:
        return None
    user = await dao.get_user_by_id(int(user_id))
    if not user:
        return None
    return user
