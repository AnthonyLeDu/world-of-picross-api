from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, ARRAY, BOOLEAN
from .user import User

GameContent = list[list[bool]]


class Game(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    difficulty: int = Field(index=True)
    content: GameContent | None = Field(
        default=None,
        sa_column=Column(ARRAY(BOOLEAN)),
    )

    creator_id: int | None = Field(default=None, foreign_key="user.id")
    creator: User | None = Relationship(back_populates="games")
