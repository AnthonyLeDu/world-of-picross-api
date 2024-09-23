from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import Session, select
from ..models.user import User, get_current_user, is_current_user, get_user
from ..models.game import Game
from ..database import engine
from ..security import (
    verify_password,
    Token,
    create_access_token,
    get_password_hash,
)
from ..config import JWT_ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()


class LoginData(BaseModel):
    email: str
    password: str


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    # user email must be under the 'username' to satisfy the OAuth2 specs.
    user = await get_user(form_data.username)
    # Verify password
    if user is None or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create and send token
    access_token_expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users")
async def get_all_users():
    with Session(engine) as session:
        users = session.exec(select(User)).all()
    return users


@router.get("/user/me")
async def get_user_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user


@router.get("/user/{id}")
async def get_one_user(id: int):
    with Session(engine) as session:
        user = session.get(User, id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User does not exist.",
        )
    return user


@router.get("/user/{id}/games")
async def get_user_games(id: int):
    with Session(engine) as session:
        games = session.select(Game).where(Game.creator_id == id).all()
    return games


@router.post("/user")
async def create_user(user: User):
    user.password = get_password_hash(user.password)
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


@router.put("/user/{id}")
async def update_user(
    current_user: Annotated[User, Depends(get_current_user)],
    id: int,
    user: User,
):
    # Be careful, all user fields must be provided otherwise default
    # ones will be used.
    # See https://fastapi.tiangolo.com/tutorial/body-updates/
    with Session(engine) as session:
        db_user = session.get(User, id)
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User does not exist.",
            )
        if current_user != db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not allowed to modify this user.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        db_user.pseudo = user.pseudo
        db_user.email = user.email  # OAuth2 spec : username = email
        db_user.password = get_password_hash(user.password)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    return db_user


@router.delete("/user/{id}")
async def delete_user(
    is_current_user: Annotated[User, Depends(is_current_user)], id: int
):
    if not is_current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You are not allowed to delete this user.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    with Session(engine) as session:
        user = session.get(User, id)
        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User does not exist.",
            )
        session.delete(user)
        session.commit()
        # TODO: Return deleted response code
