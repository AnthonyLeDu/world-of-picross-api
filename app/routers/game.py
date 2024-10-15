from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status
from ..models.game import Game, GameDetails, GameSummary
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
        game.update_clues()  # TODO: remove
        return GameDetails.model_validate(game)


@router.post("/game", status_code=status.HTTP_201_CREATED)
async def create_game(
    game: Game,
    current_user: Annotated[User, Depends(get_current_user)],
):
    game.creator_id = current_user.id  # Force current user to be the creator
    game.update_clues()
    game.update_difficulty()
    with Session(engine) as session:
        session.add(game)
        session.commit()
        session.refresh(game)
        return GameDetails.model_validate(game)


@router.put("/game/{id}")
async def update_game(
    id: int,
    game: Game,
    current_user: Annotated[User, Depends(get_current_user)],
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
        db_game.update_difficulty()
        db_game.update_clues()
        # TODO: Delete below
        # db_game.creator_id = current_user.id
        session.add(db_game)
        session.commit()
        session.refresh(db_game)
        return GameDetails.model_validate(game)


@router.delete("/game/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
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
