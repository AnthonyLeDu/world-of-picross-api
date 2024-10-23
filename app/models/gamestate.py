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

    def update_is_completed(self, goal_content: Content):
        self.is_completed = False
        if self.current_content is None or goal_content is None:
            return False
        if len(goal_content) != len(self.current_content):
            raise ValueError("Contents don't have the same amount of rows.")
        for r, row in enumerate(goal_content):
            if len(row) != len(self.current_content[r]):
                raise ValueError(
                    "Content rows don't have the same amount of cells."
                )
            for c, cell in enumerate(row):
                if cell != self.current_content[r][c]:
                    return
        self.is_completed = True


class GameStateContentIn(BaseModel):
    current_content: Content | None

    model_config = ConfigDict(from_attributes=True)


class GameStateContentOut(GameStateContentIn):
    is_completed: bool = False

    model_config = ConfigDict(from_attributes=True)
