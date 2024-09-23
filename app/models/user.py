from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from sqlmodel import Field, SQLModel, Relationship, Session, select
from ..database import engine
from .gamestate import GameState
from ..security import oauth2_scheme, TokenData
from ..config import JWT_SECRET_KEY, JWT_ALGORITHM


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    pseudo: str = Field(unique=True)
    email: str | None = Field(default=None, unique=True)
    password: str
    created_games: list["Game"] = Relationship(  # type: ignore
        back_populates="creator",
    )
    played_game_links: list[GameState] = Relationship(back_populates="user")

    @property
    def played_games_ids(self):
        return [game_state.game_id for game_state in self.played_game_links]


async def get_user(email: str):
    with Session(engine) as session:
        statement = select(User).where(User.email == email)
        return session.exec(statement).one_or_none()


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user(token_data.username)  # username = email
    if user is None:
        raise credentials_exception
    return user


async def is_current_user(
    current_user: Annotated[User, Depends(get_current_user)], user: User
):
    return current_user == user
