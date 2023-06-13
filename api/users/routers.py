from fastapi import APIRouter

from api.auth.routers import fastapi_users
from api.auth.schemes import UserRead, UserUpdate

users_api = APIRouter(
    prefix="/users",
    tags=["users"]
)
users_api.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))