from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy.dialects.postgresql import JSONB
from . import Content


class GameState(SQLModel, table=True):
    game_id: int | None = Field(
        default=None, foreign_key="game.id", primary_key=True
    )
    user_id: int | None = Field(
        default=None, foreign_key="user.id", primary_key=True
    )
    is_completed: bool = False
    current_content: Content | None = Field(
        default=None, sa_column=Column(JSONB)
    )

    game: "Game" = Relationship(back_populates="player_links")  # type: ignore
    user: "User" = Relationship(  # type: ignore
        back_populates="played_game_links"
    )


class GameStateContent(BaseModel):
    is_completed: bool = False
    current_content: Content | None

    model_config = ConfigDict(from_attributes=True)
