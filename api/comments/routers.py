import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.routers import fastapi_users
from api.comments.schemes import CreateComment, CommentRead
from db.models import Comment, User, Video
from db.session import get_async_session

comments_api = APIRouter(
    prefix="/comments",
    tags=["comments"]
)


@comments_api.get("/for_video/{video_id}")
async def get_comments(video_id: uuid.UUID,
                       db: AsyncSession = Depends(get_async_session)) -> list[CommentRead]:
    return [comment_to_commentRead(comment)
            for comment in (await db.execute(select(Comment).where(Comment.video_id == video_id))).scalars().all()]


@comments_api.post("/for_video/{video_id}", status_code=201)
async def add_comment(video_id: uuid.UUID,
                      comment: CreateComment,
                      user: User = Depends(fastapi_users.current_user(active=True, verified=True)),
                      db: AsyncSession = Depends(get_async_session)):
    flag = (await db.execute(select(Video.id).where(Video.id == video_id))).scalar()
    if flag is None:
        raise HTTPException(404)

    db.add(Comment(user_id=user.id, video_id=comment.video_id, text=comment.text))
    await db.commit()


def comment_to_commentRead(comment: Comment) -> CommentRead:
    return CommentRead(id=comment.id,
                       text=comment.text,
                       video_id=comment.video_id,
                       user_id=comment.user_id,
                       published_date=comment.published_date)
