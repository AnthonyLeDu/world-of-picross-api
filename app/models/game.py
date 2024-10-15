import copy
from random import randint
from sqlalchemy import Column
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import BaseModel, ConfigDict
from .gamestate import GameState
from .user import User, UserSummary

type Rgba = list[int | float]
type Clue = dict[str, Rgba | int]
type ClueLine = list[Clue | None]
type Clues = list[list[ClueLine]]
type LineContent = list[Rgba | None]
type Content = list[LineContent | None]


class Game(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    difficulty: int = Field(index=True)
    content: Content | None = Field(default=None, sa_column=Column(JSONB))
    clues: Clues | None = Field(default=None, sa_column=Column(JSONB))
    creator_id: int | None = Field(default=None, foreign_key="user.id")

    creator: User | None = Relationship(back_populates="created_games")
    player_links: list[GameState] = Relationship(back_populates="game")

    def update_difficulty(self):
        # TODO: algorithm to calculate difficulty
        if self.content is None:
            self.difficulty = None
        self.difficulty = randint(1, 5)

    def update_clues(self):
        def get_line_clues(line_content: LineContent):
            clue_line: ClueLine = []
            last_rgba = False
            is_first_index = True
            for rgba in line_content:
                if (
                    is_first_index is not True  # Not the firt cell
                    and rgba != None
                    and last_rgba == rgba  # Same color than previous cell
                ):
                    clue_line[-1]["count"] += 1  # Increment clue count
                else:
                    if rgba is not None:  # Add new clue
                        clue_line.append(
                            {
                                "rgba": copy.copy(rgba),
                                "count": 1,
                            }
                        )
                    last_rgba = copy.copy(rgba)
                    is_first_index = False
            if len(clue_line) == 0:
                clue_line.append(None)
            return clue_line

        if self.content is None:
            self.clues = None
            return

        # Get pivoted content for colums
        columns_content: Content = []
        for i in range(self.columns_count):
            columns_content.append(list(map(lambda row: row[i], self.content)))

        self.clues = [
            list(map(get_line_clues, self.content)),
            list(map(get_line_clues, columns_content)),
        ]

    @property
    def players_ids(self):
        return [game_state.user_id for game_state in self.player_links]

    @property
    def rows_count(self):
        if self.content is None:
            return None
        return len(self.content)

    @property
    def columns_count(self):
        if self.content is None:
            return None
        return max([len(row) for row in self.content])


class GameSummary(BaseModel):
    id: int | None
    name: str
    difficulty: int
    creator: UserSummary | None
    rows_count: int | None
    columns_count: int | None

    model_config = ConfigDict(from_attributes=True)


class GameDetails(GameSummary):
    content: Content | None
    clues: Clues | None

    model_config = ConfigDict(from_attributes=True)