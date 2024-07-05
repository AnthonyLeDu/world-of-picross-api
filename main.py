from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from server import env
from models.game import Game

GAMES_DIR = os.path.join(os.path.split(__file__)[0], 'data\\games')


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=env.allowed_origins
)

@app.get("/")
async def root() -> dict:
    return {"message": "Hello World"}


@app.get("/games")
async def get_games() -> list[dict]:
    games = []
    for filename in os.listdir(GAMES_DIR):
        with open(os.path.join(GAMES_DIR, filename), "r") as f:
            data = json.load(f)
        data["id"] = os.path.splitext(filename)[0]
        game = Game(**data)
        games.append(game.model_dump_preview)
    return games


@app.get("/game/{id}")
async def get_one_game(id: int) -> Game:
    with open(os.path.join(GAMES_DIR, str(id) + ".json"), "r") as f:
        data = json.load(f)
    data["id"] = id
    game = Game(**data)
    return game
