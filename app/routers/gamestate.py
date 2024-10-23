from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status
from ..models.gamestate import (
    GameState,
    GameStateContentIn,
    GameStateContentOut,
)
from ..models.user import User, get_current_user
from .game import get_game
from sqlmodel import Session, select
from ..database import engine

router = APIRouter()


def get_game_state(
    game_id: int,
    user_id: int,
    session: Session,
    exception_if_not_found: bool = False,
):
    game_state = (
        session.exec(
            select(GameState)
            .where(GameState.game_id == game_id)
            .where(GameState.user_id == user_id)
        )
        .unique()
        .one_or_none()
    )
    if game_state is None and exception_if_not_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Current user has no game state for given game_id "
                f"({game_id})."
            ),
        )
    return game_state


@router.get("/gamestate/{id}")
async def get_one_game_state(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
):
    with Session(engine) as session:
        game_state = get_game_state(
            id, current_user.id, session, exception_if_not_found=True
        )
        return GameStateContentOut.model_validate(game_state)


@router.post("/gamestate/{id}", status_code=status.HTTP_201_CREATED)
async def create_game_state(
    id: int,
    game_state_input: GameStateContentIn,
    current_user: Annotated[User, Depends(get_current_user)],
):
    # TODO: protect against XSRF
    with Session(engine) as session:
        game_state = get_game_state(id, current_user.id, session)
        if game_state is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Game state already exists hence cannot be created.",
            )
        game_state = GameState.model_validate(game_state_input)
        game_state.game_id = id
        game_state.user_id = current_user.id
        # Update completion from goal game content
        game = get_game(id, session, exception_if_not_found=True)
        game_state.update_is_completed(game.content)
        # Pust to DB
        session.add(game_state)
        session.commit()
        session.refresh(game_state)
        return GameStateContentOut.model_validate(game_state)


@router.put("/gamestate/{id}")
async def update_game_state(
    id: int,
    game_state_input: GameStateContentIn,
    current_user: Annotated[User, Depends(get_current_user)],
):
    # TODO: protect against XSRF
    # Be careful, all GameState fields must be provided otherwise default
    # ones will be used.
    # See https://fastapi.tiangolo.com/tutorial/body-updates/
    with Session(engine) as session:
        db_game_state = get_game_state(
            id, current_user.id, session, exception_if_not_found=True
        )
        # Update completion from goal game content
        game = get_game(id, session, exception_if_not_found=True)
        db_game_state.current_content = game_state_input.current_content
        db_game_state.update_is_completed(game.content)
        # Pust to DB
        session.add(db_game_state)
        session.commit()
        session.refresh(db_game_state)
        return GameStateContentOut.model_validate(db_game_state)


@router.delete("/gamestate/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game_state(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
):
    # TODO: protect against XSRF
    with Session(engine) as session:
        game_state = get_game_state(
            id, current_user.id, session, exception_if_not_found=True
        )
        session.delete(game_state)
        session.commit()
