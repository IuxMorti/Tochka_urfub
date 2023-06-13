import uuid

from fastapi_users import FastAPIUsers
from fastapi import APIRouter
from db.models import User
from .strategy import auth_backend
from .manager import get_user_manager

from .schemes import UserRead, UserCreate, UserUpdate

auth_api = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

auth_api.include_router(fastapi_users.get_verify_router(UserRead))
auth_api.include_router(fastapi_users.get_reset_password_router())
auth_api.include_router(fastapi_users.get_auth_router(auth_backend))
auth_api.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
