from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root() -> dict:
    return {"message": "Hello World"}


@app.get("/games/{game_id}")
async def get_one_game(game_id: int) -> dict:
    return {"game": game_id}
