from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status
from ..models.game import (
    Game,
    GameDetails,
    GameSummaryWithCreator,
    GameInput,
    GameSummary,
)
from ..models.user import User, get_current_user
from sqlmodel import Session, select
from ..database import engine

router = APIRouter()


def get_game(id: int, session: Session, exception_if_not_found: bool = False):
    game = session.get(Game, id)
    if game is None and exception_if_not_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No game found for given id ({id}).",
        )
    return game


@router.get("/games")
async def get_all_games():
    with Session(engine) as session:
        games = session.exec(select(Game)).all()
        return [GameSummaryWithCreator.model_validate(game) for game in games]


@router.get("/games/me")
async def get_current_user_games(
    current_user: Annotated[User, Depends(get_current_user)],
):
    with Session(engine) as session:
        games = session.exec(
            select(Game).where(Game.creator_id == current_user.id)
        ).all()
        return [GameSummary.model_validate(game) for game in games]


@router.get("/game/{id}")
async def get_one_game(id: int):
    with Session(engine) as session:
        game = get_game(id, session, exception_if_not_found=True)
        # TODO: remove when clues will be generated at game post/put
        game.update_clues()
        return GameDetails.model_validate(game)


@router.post("/game", status_code=status.HTTP_201_CREATED)
async def create_game(
    game_input: GameInput,
    current_user: Annotated[User, Depends(get_current_user)],
):
    # TODO: protect against XSRF
    game = Game.model_validate(game_input)
    game.creator_id = current_user.id  # Make current user the creator
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
    game_input: GameInput,
    current_user: Annotated[User, Depends(get_current_user)],
):
    # TODO: protect against XSRF
    # Be careful, all Game fields must be provided otherwise default
    # ones will be used.
    # See https://fastapi.tiangolo.com/tutorial/body-updates/
    with Session(engine) as session:
        db_game = get_game(id, session, exception_if_not_found=True)
        # Validate that user owns the game
        if db_game.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Current user is not allowed to modify this game.",
            )
        db_game.name = game_input.name
        db_game.content = game_input.content
        db_game.update_difficulty()
        db_game.update_clues()

        session.add(db_game)
        session.commit()
        session.refresh(db_game)
        return GameDetails.model_validate(db_game)


@router.delete("/game/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
):
    # TODO: protect against XSRF
    with Session(engine) as session:
        game = get_game(id, session, exception_if_not_found=True)
        if game.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Current user is not allowed to delete this game.",
            )
        session.delete(game)
        session.commit()
