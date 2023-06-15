import uuid
from datetime import datetime

from pydantic import BaseModel


class CommentRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    video_id: uuid.UUID
    text: str
    published_date: datetime
    username:str

class CreateComment(BaseModel):
    text: str
