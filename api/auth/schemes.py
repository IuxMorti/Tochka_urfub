import datetime
import typing
import uuid
from typing import Optional

from fastapi_users import schemas
from fastapi_users.schemas import CreateUpdateDictModel, BaseUser
from pydantic import EmailStr


class UserRead(BaseUser[uuid.UUID]):
    username: str
    register_date: datetime.datetime
    url_photo: typing.Union[str, None]


class UserCreate(CreateUpdateDictModel):
    username: str
    password: str
    email: EmailStr


class UserUpdate(CreateUpdateDictModel):
    username: Optional[str]
    password: Optional[str]
    email: Optional[EmailStr]
