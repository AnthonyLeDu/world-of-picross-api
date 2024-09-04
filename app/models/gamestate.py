from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, ARRAY, BOOLEAN
from . import GameContent


class GameState(SQLModel, table=True):
    game_id: int | None = Field(
        default=None, foreign_key="game.id", primary_key=True
    )
    user_id: int | None = Field(
        default=None, foreign_key="user.id", primary_key=True
    )
    is_completed: bool = False
    current_content: GameContent | None = Field(
        default=None,
        sa_column=Column(ARRAY(BOOLEAN)),
    )

    game: "Game" = Relationship(back_populates="player_links")  # type: ignore
    user: "User" = Relationship(  # type: ignore
        back_populates="played_game_links"
    )
