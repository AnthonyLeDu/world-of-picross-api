from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status
from ..models.gamestate import GameState, GameStateContent
from ..models.user import User, get_current_user
from sqlmodel import Session, select
from ..database import engine

router = APIRouter()


async def get_game_state(game_id: int, user_id: int, session: Session):
    game_state = (
        session.exec(
            select(GameState)
            .where(GameState.game_id == game_id)
            .where(GameState.user_id == user_id)
        )
        .unique()
        .one_or_none()
    )
    if game_state is None:
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
        game_state = await get_game_state(id, current_user.id, session)
        return GameStateContent.model_validate(game_state)


@router.post("/gamestate/{id}", status_code=status.HTTP_201_CREATED)
async def create_game_state(
    id: int,
    game_state_input: GameStateContent,
    current_user: Annotated[User, Depends(get_current_user)],
):
    # TODO: protect against XSRF
    game_state = GameState.model_validate(game_state_input)
    game_state.game_id = id
    game_state.user_id = current_user.id
    with Session(engine) as session:
        session.add(game_state)
        session.commit()
        session.refresh(game_state)
        return GameStateContent.model_validate(game_state)


@router.put("/gamestate/{id}")
async def update_game_state(
    id: int,
    game_state_input: GameStateContent,
    current_user: Annotated[User, Depends(get_current_user)],
):
    # TODO: protect against XSRF
    # Be careful, all GameState fields must be provided otherwise default
    # ones will be used.
    # See https://fastapi.tiangolo.com/tutorial/body-updates/
    with Session(engine) as session:
        db_game_state = await get_game_state(id, current_user.id, session)
        db_game_state.is_completed = game_state_input.is_completed
        db_game_state.current_content = game_state_input.current_content
        session.add(db_game_state)
        session.commit()
        session.refresh(db_game_state)
        return GameStateContent.model_validate(db_game_state)


@router.delete("/gamestate/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game_state(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
):
    # TODO: protect against XSRF
    with Session(engine) as session:
        game_state = await get_game_state(id, current_user.id, session)
        session.delete(game_state)
        session.commit()
