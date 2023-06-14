import uuid
from pydantic import BaseModel


class CreateComment(BaseModel):
    video_id: uuid.UUID
    text: str
