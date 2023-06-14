import typing
import uuid

import sqlalchemy
from fastapi import APIRouter, Depends, Request, HTTPException, UploadFile
import jwt
from fastapi.params import Header
from pydantic import Required
from sqlalchemy import select, insert, exists, update
from sqlalchemy.ext.asyncio import AsyncSession
import redis
from starlette import status

from api.auth.routers import fastapi_users
from api.common.schemes import pagination_params
from api.utils.redis_utils import RedisKeys
from api.utils.s3_utils import upload_video, upload_image
from api.videos.schemes import Total, VideoModel, VideoUpdate, VideoList
from config import SECRET
from db.models import User, Video
from db.session import get_async_session, get_redis_async_session

videos_api = APIRouter(
    prefix="/videos",
    tags=["Videos"]
)

MAX_FILE_SIZE = 1024 * 1024 * 700  # 700mb
MAX_IMAGE_SIZE = 1024 * 1024 * 10


class MaxBodySizeException(Exception):
    def __init__(self, body_len: int):
        self.body_len = body_len


@videos_api.get("/my")
async def my_videos(
        page_params: dict = Depends(pagination_params),
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(fastapi_users.current_user(active=True)),
        red: redis.Redis = Depends(get_redis_async_session)) -> list[VideoModel]:
    res = await db.execute(select(Video).where(Video.owner_id == user.id)
                           .offset(page_params["offset"]).limit(page_params["limit"]))

    return [await video_to_model_video(video, red) for video in res.scalars().all()]


@videos_api.get("/")
async def get_videos(page_params: dict = Depends(pagination_params),
                     db: AsyncSession = Depends(get_async_session),
                     red: redis.Redis = Depends(get_redis_async_session)) -> VideoList:
    videos = await db.execute(
        select(Video).where(not Video.is_private).offset(page_params["offset"]).limit(page_params["limit"]))
    total = await db.execute(
        select(sqlalchemy.func.count()).select_from(Video).where(Video.is_private == False).offset(
            page_params["offset"]).limit(page_params["limit"]))

    return VideoList(videos=[await video_to_model_video(video, red) for video in videos.scalars().all()],
                     total=total.scalar())


@videos_api.post("/", status_code=status.HTTP_201_CREATED)
async def add_video(request: Request,
                    filename: str = Header(Required),
                    types: str = Header(Required),
                    user: User = Depends(fastapi_users.current_user(active=True, verified=True)),
                    db: AsyncSession = Depends(get_async_session),
                    red: redis.Redis = Depends(get_redis_async_session)):
    if types.split("/")[1] not in ["mp4"]:
        raise HTTPException(status_code=415, detail={"message": " supported: mp4"})
    if int(request.headers.get("Content-Length")) > MAX_FILE_SIZE:
        raise MaxBodySizeException(body_len=int(request.headers.get("Content-Length")))

    url = await upload_video(request, filename)

    video = Video(url_video=url, owner_id=user.id, name=filename)
    db.add(video)
    await db.commit()
    return await video_to_model_video(video, red)


@videos_api.delete("/{_id}", status_code=204)
async def delete_video(_id: uuid.UUID,
                       user: User = Depends(fastapi_users.current_user(active=True, verified=True)),
                       db: AsyncSession = Depends(get_async_session),
                       red: redis.Redis = Depends(get_redis_async_session)):
    video = (await db.execute(select(Video).where(Video.id == _id))).scalar()
    if video is None:
        raise HTTPException(404)
    if video.owner_id != user.id:
        raise HTTPException(403)
    await red.delete(RedisKeys.video_views(video.id))
    await red.delete(RedisKeys.video_likes(video.id))
    await red.delete(RedisKeys.video_dislike(video.id))
    await db.delete(video)
    await db.commit()


@videos_api.patch("/{_id}")
async def update_video_info(_id: uuid.UUID,
                            video_update: VideoUpdate,
                            db: AsyncSession = Depends(get_async_session),
                            red: redis.Redis = Depends(get_redis_async_session),
                            user: User = Depends(fastapi_users.current_user(active=True, verified=True))):
    video: Video = (await db.execute(select(Video).where(Video.id == _id))).scalar()
    if video is None:
        raise HTTPException(404)

    if video.owner_id != user.id:
        raise HTTPException(403)

    await db.execute(update(Video).where(Video.id == _id).values(**dict((filter(lambda t: t[1] is not None,
                                                                                video_update.dict().items())))))
    await db.commit()

    print()


@videos_api.get("/{_id}")
async def get_video(_id: uuid.UUID,
                    request: Request,
                    db: AsyncSession = Depends(get_async_session),
                    red: redis.Redis = Depends(get_redis_async_session)) -> VideoModel:
    auth_token = request.headers.get("Authorization")
    video: Video = (await db.execute(select(Video).where(Video.id == _id))).scalar()
    if video is None:
        raise HTTPException(404)

    if auth_token is None:
        if video.is_private:
            raise HTTPException(403)
    else:
        res = jwt.decode(auth_token.split()[1], key=SECRET, algorithms=["HS256"], audience=["fastapi-users:auth"])
        if video.is_private and uuid.UUID(res["sub"]) != video.owner_id:
            raise HTTPException(403)
        await red.sadd(RedisKeys.video_views(video.id), res["sub"])
        await red.sadd(RedisKeys.user_views(res["sub"]), str(video.id))

    return await video_to_model_video(video, red)


@videos_api.post("/{_id}/like", status_code=204)
async def like(_id: uuid.UUID, red: redis.Redis = Depends(get_redis_async_session),
               db: AsyncSession = Depends(get_async_session),
               user: User = Depends(fastapi_users.current_user(active=True))):
    flag = (await db.execute(select(Video.id).where(Video.id == _id))).scalar()
    if flag is None:
        await red.srem(RedisKeys.user_views(user.id), str(_id))
        raise HTTPException(404)
    await toggle_dislike(red, _id, user.id, remove=True)
    return await toggle_like(red, _id, user.id)


@videos_api.get("/my/likes")
async def get_my_likes(red: redis.Redis = Depends(get_redis_async_session),
                       db: AsyncSession = Depends(get_async_session),
                       user: User = Depends(fastapi_users.current_user(active=True))) -> VideoList:
    likes = await red.smembers(RedisKeys.user_likes(user.id))
    res = (await db.execute(select(Video).where(Video.id.in_(likes)))).scalars().all()
    return VideoList(videos=[await video_to_model_video(video, red) for video in res],
                     total=len(likes))


@videos_api.get("/my/views")
async def get_my_views(red: redis.Redis = Depends(get_redis_async_session),
                       db: AsyncSession = Depends(get_async_session),
                       user: User = Depends(fastapi_users.current_user(active=True))) -> VideoList:
    views = await red.smembers(RedisKeys.user_views(user.id))
    res = (await db.execute(select(Video).where(Video.id.in_(views)))).scalars().all()
    return VideoList(videos=[await video_to_model_video(video, red) for video in res],
                     total=len(views))


@videos_api.post("/{_id}/dislike")
async def dislike(_id: uuid.UUID,
                  red: redis.Redis = Depends(get_redis_async_session),
                  db: AsyncSession = Depends(get_async_session),
                  user: User = Depends(fastapi_users.current_user(active=True))):
    flag = (await db.execute(select(Video.id).where(Video.id == _id))).scalar()
    if flag is None:
        await red.srem(RedisKeys.user_views(user.id), str(_id))
        raise HTTPException(404)

    await toggle_like(red, _id, user.id, remove=True)
    return await toggle_dislike(red, _id, user.id)


@videos_api.get("/{_id}/like-and-dislike")
async def get_like_and_dislike(_id: uuid.UUID,
                               red: redis.Redis = Depends(get_redis_async_session)):
    return {"likes": await red.scard(RedisKeys.video_likes(_id)),
            "dislike": await red.scard(RedisKeys.video_dislike(_id))}


@videos_api.post("/{_id}/preview")
async def update_preview(_id: uuid.UUID, preview: UploadFile,
                         user: User = Depends(fastapi_users.current_user(active=True, verified=True)),
                         db: AsyncSession = Depends(get_async_session)):
    if preview.content_type.split("/")[0] != "image":
        raise HTTPException(status_code=415, detail={"message": " supported only images"})
    if preview.size > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, detail={"message": " supported only images"})

    video: Video = (await db.execute(select(Video).where(Video.id == _id))).scalar()
    if video is None:
        raise HTTPException(404)
    if video.owner_id != user.id:
        raise HTTPException(403)

    res = await upload_image(preview)
    await db.execute(update(Video).where(Video.id == _id).values(preview=res))
    await db.commit()


async def toggle_like(red: redis.Redis, id_video: uuid.UUID, id_user: uuid.UUID, remove=False):
    key = RedisKeys.video_likes(id_video)
    user_key = str(id_user)
    if await red.sismember(key, user_key):
        await red.srem(key, user_key)
        await red.srem(RedisKeys.user_likes(id_user), str(id_video))
    elif not remove:
        await red.sadd(key, user_key)
        await red.sadd(RedisKeys.user_likes(id_user), str(id_video))

    return await red.scard(key)


async def toggle_dislike(red: redis.Redis, id_video: uuid.UUID, id_user: uuid.UUID, remove=False):
    key = RedisKeys.video_dislike(id_video)
    user_key = str(id_user)
    if await red.sismember(key, user_key):
        await red.srem(key, user_key)
    elif not remove:
        await red.sadd(key, user_key)
    return await red.scard(key)


async def video_to_model_video(video: Video, red: redis.Redis) -> VideoModel:
    return VideoModel(
        id=video.id,
        name=video.name,
        url_video=video.url_video,
        description=video.description,
        is_private=video.is_private,
        preview=video.preview,
        published_date=video.published_date,
        owner_id=video.owner_id,
        count_view=await red.scard(RedisKeys.video_views(video.id))
    )


print()
