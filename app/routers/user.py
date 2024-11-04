from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse, Response
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import Session, select
from ..models.user import (
    User,
    PrivateUser,
    PublicUser,
    get_current_user,
    get_user,
)
from ..models.game import Game, GameSummaryWithCreator
from ..database import engine
from ..security import (
    verify_password,
    Token,
    create_access_token,
    get_password_hash,
)
from ..config import JWT_ACCESS_TOKEN_EXPIRE_MINUTES, JWT_COOKIE_NAME

router = APIRouter()


class LoginData(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login_with_credentials(
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
    expires = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=expires
    )
    response = Response()
    response.set_cookie(
        key=JWT_COOKIE_NAME,
        value=access_token,
        expires=expires,
        secure=True,
        httponly=True,
        samesite="strict",
    )
    return response


@router.get("/login")
async def login_with_cookie(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user


@router.get("/logout")
async def logout(
    response: Response,
):
    response.delete_cookie(JWT_COOKIE_NAME)
    response.status_code = 200
    return response


@router.get("/users")
async def get_all_users():
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        # public_users = [user.to_public_user() for user in users]
        return [PublicUser.model_validate(user) for user in users]


@router.get("/user/me", response_model=PrivateUser)
async def get_user_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user


@router.get("/user/{id}", response_model=PublicUser)
async def get_one_user(id: int):
    with Session(engine) as session:
        user = session.get(User, id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{id}' does not exist.",
            )
        return PublicUser.model_validate(user)


@router.get("/user/{id}/games")
async def get_games_created_by_user(id: int):
    with Session(engine) as session:
        games = session.exec(select(Game).where(Game.creator_id == id)).all()
        return [GameSummaryWithCreator.model_validate(game) for game in games]


@router.post("/user", status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    user.password = get_password_hash(user.password)
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return PrivateUser.model_validate(user)


@router.put("/user/{id}", response_model=PrivateUser)
async def update_user(
    id: int,
    user: User,
    current_user: Annotated[User, Depends(get_current_user)],
):
    # TODO: protect against XSRF
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
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to modify this user.",
            )
        db_user.pseudo = user.pseudo
        db_user.email = user.email  # OAuth2 spec : username = email
        db_user.password = get_password_hash(user.password)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return PrivateUser.model_validate(db_user)


@router.delete("/user/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: int,
    current_user: Annotated[User, Depends(get_current_user)],
):
    # TODO: protect against XSRF
    if not current_user.id == id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to delete this user.",
        )
    with Session(engine) as session:
        user = session.get(User, id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{id}' does not exist.",
            )
        session.delete(user)
        session.commit()
