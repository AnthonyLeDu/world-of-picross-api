from sqlmodel import Field, SQLModel, Relationship
from .gamestate import GameState


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    pseudo: str = Field(unique=True)
    email: str = Field(unique=True)
    password: str
    created_games: list["Game"] = Relationship(  # type: ignore
        back_populates="creator",
    )
    played_game_links: list[GameState] = Relationship(back_populates="user")

    @property
    def played_games_ids(self):
        return [game_state.game_id for game_state in self.played_game_links]
