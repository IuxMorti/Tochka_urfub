import uuid
import datetime
from typing import Union, Optional

from pydantic import BaseModel


class Total(BaseModel):
    total: int


class VideoModel(BaseModel):
    id: uuid.UUID
    name: str
    url_video: str
    description: Union[str, None]
    is_private: bool
    preview: Union[str, None]
    published_date: datetime.datetime
    owner_id: uuid.UUID
    count_view: int


class VideoUpdate(BaseModel):
    name: str
    description: Optional[str]
    is_private: Optional[bool]


class VideoList(BaseModel):
    videos: list[VideoModel]
    total: int