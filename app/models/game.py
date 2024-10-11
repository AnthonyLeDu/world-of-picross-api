from sqlalchemy import Column
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import BaseModel, ConfigDict
from .gamestate import GameState
from .user import User, UserSummary


class Game(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    difficulty: int = Field(index=True)
    content: dict | None = Field(default=None, sa_column=Column(JSONB))
    creator_id: int | None = Field(default=None, foreign_key="user.id")

    creator: User | None = Relationship(back_populates="created_games")
    player_links: list[GameState] = Relationship(back_populates="game")

    @property
    def players_ids(self):
        return [game_state.user_id for game_state in self.player_links]


class GameSummary(BaseModel):
    id: int | None
    name: str
    difficulty: int
    creator: UserSummary | None

    model_config = ConfigDict(from_attributes=True)
