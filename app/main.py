from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import config

# from .database import init_db
from .routers import game, user, gamestate


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
)

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}


app.include_router(game.router)
app.include_router(user.router)
app.include_router(gamestate.router)


# if __name__ == "__main__":
#     init_db()

# TODO: Define some indexes ? (https://sqlmodel.tiangolo.com/tutorial/indexes/)
