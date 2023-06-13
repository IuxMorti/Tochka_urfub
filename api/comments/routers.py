from fastapi import APIRouter

comments_api = APIRouter(
    prefix="/comments",
    tags=["comments"]
)


#@comments_api.get("/")
#async def get_comments()

#likes, dislikes, write, change, get_coments, likes