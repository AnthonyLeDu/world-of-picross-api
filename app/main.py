from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from . import config
from .database import init_db
from .models.game import Game
from sqlmodel import Session, select
from .database import engine


GAMES_DIR = os.path.join(os.path.split(__file__)[0], "data\\games")


app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=config.ALLOWED_ORIGINS)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/games")
async def get_all_games():
    with Session(engine) as session:
        games = session.exec(select(Game)).all()
    return games


@app.get("/game/{id}")
async def get_one_game(id: int) -> Game:
    with Session(engine) as session:
        game = session.exec(
            select(Game).where(Game.id == id)
        ).first()
    return game


@app.post("/game")
async def create_game(game: Game):
    with Session(engine) as session:
        session.add(game)
        session.commit()
        session.refresh(game)
    return game


# if __name__ == "__main__":
#     init_db()
