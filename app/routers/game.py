from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status
from ..models.game import Game, GameSummary
from ..models.user import User, get_current_user
from sqlmodel import Session, select
from ..database import engine

router = APIRouter()


@router.get("/games")
async def get_all_games():
    with Session(engine) as session:
        statement = select(Game)
        games = session.exec(statement).all()
        return [GameSummary.model_validate(game) for game in games]


@router.get("/game/{id}")
async def get_one_game(id: int):
    with Session(engine) as session:
        game = session.get(Game, id)
        if game is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No game found for given id ({id}).",
            )
        return game


@router.post("/game", status_code=status.HTTP_201_CREATED)
async def create_game(
    current_user: Annotated[User, Depends(get_current_user)], game: Game
):
    game.creator_id = current_user.id  # Force current user to be the creator
    with Session(engine) as session:
        session.add(game)
        session.commit()
        session.refresh(game)
        return game


@router.put("/game/{id}")
async def update_game(
    current_user: Annotated[User, Depends(get_current_user)],
    id: int,
    game: Game,
):
    # Be careful, all Game fields must be provided otherwise default
    # ones will be used.
    # See https://fastapi.tiangolo.com/tutorial/body-updates/
    with Session(engine) as session:
        db_game = session.get(Game, id)
        if db_game is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No game found for given id ({id}).",
            )
        # Validate that user owns the game
        if db_game.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Current user is not allowed to modify this game.",
            )
        db_game.name = game.name
        db_game.difficulty = game.difficulty
        db_game.content = game.content
        db_game.creator_id = current_user.id
        session.add(db_game)
        session.commit()
        session.refresh(db_game)
        return db_game


@router.delete("/game/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(
    current_user: Annotated[User, Depends(get_current_user)], id: int
):
    with Session(engine) as session:
        game = session.get(Game, id)
        if game is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No game found for given id ({id}).",
            )
        if game.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Current user is not allowed to delete this game.",
            )
        session.delete(game)
        session.commit()
