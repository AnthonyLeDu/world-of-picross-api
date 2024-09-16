from fastapi import APIRouter, HTTPException
from ..models.user import User
from ..models.game import Game
from sqlmodel import Session, select
from ..database import engine

router = APIRouter()


@router.get("/games")
async def get_all_games():
    with Session(engine) as session:
        statement = select(Game)
        games = session.exec(statement).all()
        return games


@router.get("/game/{id}")
async def get_game(id: int):
    with Session(engine) as session:
        game = session.get(Game, id)
        if game is None:
            raise HTTPException(
                status_code=404, detail=f"No game found for given id ({id})."
            )
        return game


@router.post("/game")
async def create_game(game: Game):
    with Session(engine) as session:
        session.add(game)
        session.commit()
        session.refresh(game)
        return game


@router.put("/game/{id}")
async def update_game(id: int, game: Game):
    # Be careful, all Game fields must be provided otherwise default
    # ones will be used.
    # See https://fastapi.tiangolo.com/tutorial/body-updates/
    with Session(engine) as session:
        db_game = session.get(Game, id)
        if db_game is None:
            return  # TODO: Return appropriate response (code)
        db_game.name = game.name
        db_game.content = game.content
        db_game.difficulty = game.difficulty
        db_game.creator_id = game.creator_id
        session.add(db_game)
        session.commit()
        session.refresh(db_game)
        return db_game


@router.delete("/game/{id}")
async def delete_game(id: int):
    with Session(engine) as session:
        game = session.get(Game, id)
        if game is not None:
            session.delete(game)
            session.commit()
            # TODO: Return deleted response code
    # TODO: Return 404 response
