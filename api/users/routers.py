from fastapi import APIRouter, Depends

from api.auth.routers import fastapi_users
from api.auth.schemes import UserRead, UserUpdate
from db.models import User

users_api = APIRouter(
    prefix="/users",
    tags=["users"]
)
users_api.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))


@users_api.patch("/change-avatar")
async def change_avatar(user: User = Depends(fastapi_users.current_user(active=True))):
    pass
