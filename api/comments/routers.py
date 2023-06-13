from fastapi import APIRouter

comments_api = APIRouter(
    prefix="/comments",
    tags=["comments"]
)


#@comments_api.get()

#likes, dislikes, write, change, get_coments, likes