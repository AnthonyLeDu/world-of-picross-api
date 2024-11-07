import jwt
from sqlalchemy.orm import joinedload
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status, Form
from pydantic import BaseModel, ConfigDict
from sqlmodel import Field, SQLModel, Relationship, Session, select
from ..database import engine
from .gamestate import GameState
from ..security import cookie_scheme, TokenData
from ..config import JWT_SECRET_KEY, JWT_ALGORITHM


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    pseudo: str = Field(unique=True)
    username: str | None = Field(unique=True)  # email
    password: str
    created_games: list["Game"] = Relationship(  # type: ignore
        back_populates="creator",
    )
    played_game_links: list[GameState] = Relationship(back_populates="user")

    @property
    def created_games_ids(self):
        return [game.id for game in self.created_games]

    @property
    def played_games_ids(self):
        return [game_state.game_id for game_state in self.played_game_links]


class UserRegisterInput(BaseModel):
    pseudo: str
    username: str  # email
    password: str


class UserSummary(BaseModel):
    id: int | None
    pseudo: str

    model_config = ConfigDict(from_attributes=True)


class PublicUser(UserSummary):
    created_games_ids: list[int]  # type: ignore

    model_config = ConfigDict(from_attributes=True)


class PrivateUser(PublicUser):
    username: str | None
    played_games_ids: list[int]

    model_config = ConfigDict(from_attributes=True)


async def get_user(username: str):
    with Session(engine) as session:
        statement = (
            select(User)
            .options(
                joinedload(User.played_game_links),
                joinedload(User.created_games),
            )
            .where(User.username == username)
        )
        return session.exec(statement).unique().one_or_none()


async def get_current_user_or_none(token: str = Depends(cookie_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
    except InvalidTokenError:
        return None
    user = await get_user(token_data.username)
    return user


async def get_current_user(token: str = Depends(cookie_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = await get_current_user_or_none(token)
    if user is None:
        raise credentials_exception
    return user
