
from fastapi import FastAPI,APIRouter
from starlette.middleware.cors import CORSMiddleware


from api.auth.routers import auth_api
from api.comments.routers import comments_api
from api.users.routers import users_api
from api.videos.routers import videos_api


app = FastAPI()


origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_v1 = APIRouter(prefix="/api/v1", tags=["v1"])
api_v1.include_router(auth_api)
api_v1.include_router(videos_api)
api_v1.include_router(users_api)
api_v1.include_router(comments_api)

app.include_router(api_v1, prefix="")

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', port=6379, reload=True)
